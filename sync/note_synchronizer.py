import re
from log import log
import time
from sync.database import Database
from sync.file_manager import FileManager
from sync.image_handler import ImageHandler
from sync.image_uploader import ImageUploader
from sync.note import Note
from sync.note_parser_factory import NoteParserFactory
from sync.note_property import NoteProperty
from sync.parsed_note import ParsedNote
from sync.wiz_open_api import WizOpenApi


class NoteSynchronizer:
    # 同步的步长
    PAGE_SIZE = 200
    ATTACHMENT_DOWNLOAD_MAX_ATTEMPTS = 3
    ATTACHMENT_DOWNLOAD_RETRY_SLEEP_S = 1

    def __init__(self, api_client: WizOpenApi, db: Database):
        self.api_client = api_client
        self.db = db

    def synchronize_notes(self):
        log.info('synchronize_notes to db start')
        # 从 wiz 获取待同步记录到db
        self._sync_from_wiz_to_db()
        # 分页获取未同步的笔记
        unsync_records = self.db.get_unsync_note_list(0, self.PAGE_SIZE)
        # 同步笔记到到本地
        while unsync_records:
            self._sync_note_to_local(unsync_records)
            # get_next_max_version
            max_version = max([record['id'] for record in unsync_records]) if unsync_records else 99999999
            log.info(f'unsync_records max_version: {max_version}')
            unsync_records = self.db.get_unsync_note_list(max_version, self.PAGE_SIZE)
        log.info('synchronize_notes to db end')

    def _download_img_if_absent(self, record, need_upload_images):
        # 获取本地不存在的图片文件
        not_in_local_img = FileManager.get_not_in_local_img(record, need_upload_images)
        if not not_in_local_img:
            return

        # 根据笔记的类型, 调用 wiz api 获取授权下载地址, 获取二进制内容保存到本地
        if not Note.is_collaboration_note(record['type']):
            # 如果是普通笔记, 直接获取所有图片的上传地址
            detail_resp = self.api_client.get_note_detail(record['doc_guid'])
            resources = detail_resp['resources']
            log.info(f'resources: {resources}')

            # resources 是一个list, 存在属性name和url
            resources_map = {res['name']: res['url'] for res in resources if 'name' in res and 'url' in res}
            log.info(f'Built resources_map with {len(resources_map)} items.')

            for img_name in not_in_local_img:
                if img_name in resources_map:
                    img_url = resources_map[img_name]
                    FileManager.download_img_from_url(record, img_name, img_url)
                else:
                    log.warning(f"Image '{img_name}' needed but not found in resources list for doc {record.get('doc_guid', 'N/A')}")
        else:
            # 如果是协作笔记, 需要循环获取所有图片的上传地址
            token = self.api_client.get_collaboration_token(record['doc_guid'])
            for img_file_name in need_upload_images:
                # 如果图片不存在 api 获取图片内容, 将图片下载到本地
                img_byte = self.api_client.get_collaboration_image_byte(token, record['doc_guid'], img_file_name)
                FileManager.download_img_from_byte(record, img_file_name, img_byte)

    def _save_img_and_get_url(self, record: dict, need_upload_images: list[str]) -> dict[str, str]:
        """
        保存并上传图片, 获取没有上传图片的<图片名称, 上传地址>
        :param record: 笔记记录
        :param need_upload_images: 需要上传的图片集合
        :return: 没有上传图片的<图片名称, 上传地址>
        """
        # 如果需要上传图片的集合为空, 直接返回空dict
        if not need_upload_images:
            return {}

        # db查询 判断哪些图片没有上传过
        uploaded_images = self.db.get_uploaded_images(record['doc_guid'], need_upload_images)
        need_upload_images = list( set(need_upload_images) - set(uploaded_images) )
        log.info(f'now need_upload_images: {need_upload_images}')

        # 定义 ret_map key: 图片名称 value: 图片上传地址
        ret_map = {}
        # 如果图片不存在则下载图片
        self._download_img_if_absent(record, need_upload_images)
        for img_file_name in need_upload_images:
            # 插入上传记录
            self.db.create_image_upload_record(record['doc_guid'], img_file_name)
            try:
                # 获取图片上传地址
                uploaded_url = ImageHandler.handle(record, img_file_name)
                # 更新上传记录的状态
                self.db.update_img_sync_status(record['doc_guid'], img_file_name, sync_status=True, fail_reason='', upload_url=uploaded_url)
                # 将图片上传地址添加到 ret_map 中
                ret_map[img_file_name] = uploaded_url
            except Exception as e:
                # 更新上传记录的状态
                self.db.update_img_sync_status(record['doc_guid'], img_file_name, sync_status=False, fail_reason=str(e), upload_url='')
        return ret_map

    def _sync_single_note_to_local(self, record):
        log.info(f'开始执行同步 doc_guid: {record["doc_guid"]} title: {record["title"]}')
        # 根据笔记的类型，获取不同类型的解析器
        parser = NoteParserFactory.create_parser(record['type'], record['title'])

        try:
            # 获取笔记的原始内容
            origin_content = self._get_note_origin_content(record['type'], record['doc_guid'])

            # 使用解析器解析笔记，将笔记转化为md, 并提取笔记中需要上传的图片
            parsed_note = parser.process_content(origin_content)
            # 上传并获取上传图片地址
            origin_img_image_url_map = self._save_img_and_get_url(record, parsed_note.need_upload_images)

            # 替换笔记中的上传图片地址
            parsed_note.replace_image_url(origin_img_image_url_map)

            # 处理笔记附件方法
            attachment_fail_reason = self._process_note_attachment(record, parsed_note)

            # 拼接笔记属性和 md 原文，写入本地文件中
            note_content = parsed_note.content
            if not isinstance(note_content, str):
                raise Exception(
                    f"parsed_note.content must be str, got {type(note_content).__name__}"
                )
            note_prop = NoteProperty.from_sync_record(record).to_string()
            joined_note_content = note_prop + note_content
            FileManager.save_md_to_file(record['category'], record['title'], joined_note_content)

            # 更新笔记的同步状态
            if attachment_fail_reason:
                self.db.update_note_sync_status(record['doc_guid'], sync_status=False, fail_reason=attachment_fail_reason)
            else:
                self.db.update_note_sync_status(record['doc_guid'], sync_status=True, fail_reason='')
        except Exception as e:
            log.exception('sync_single_note_to_local error: ')
            # 出现异常时更新同步状态和错误原因
            error_reason = str(e)
            self.db.update_note_sync_status(record['doc_guid'], sync_status=False, fail_reason=error_reason)

    def _download_with_retry(self, label, download_func):
        max_attempts = self.ATTACHMENT_DOWNLOAD_MAX_ATTEMPTS
        for attempt in range(1, max_attempts + 1):
            try:
                if attempt > 1:
                    log.info(f'下载重试({attempt}/{max_attempts}): {label}')
                return download_func()
            except Exception as e:
                log.warning(f'下载失败({attempt}/{max_attempts}): {label}, 错误: {type(e).__name__}: {e}')
                if attempt >= max_attempts:
                    raise
                time.sleep(self.ATTACHMENT_DOWNLOAD_RETRY_SLEEP_S * attempt)
    
    def _extract_attachment_links_from_markdown(self, content):
        """
        从markdown内容中提取附件链接，使用特殊标记确保准确性
        :param content: markdown内容
        :return: 附件文件名列表
        """
        # 先移除代码块内容，避免提取代码块中的链接
        import re
        # 移除代码块（```...```）
        content_without_code = re.sub(r'```[\s\S]*?```', '', content)
        # 移除行内代码（`...`）
        content_without_code = re.sub(r'`[^`]*`', '', content_without_code)
        
        # 只匹配包含特殊标记的附件链接，避免误提取普通链接
        # 使用负向前瞻排除图片语法，确保不匹配 ![text](wiz-collab-attachment://...)
        pattern = r'(?<!!)\[([^\]]*)\]\(wiz-collab-attachment://([^)]+)\)'
        matches = re.findall(pattern, content_without_code)
        # 返回链接URL部分（文件名），过滤掉空文件名
        return [match[1] for match in matches if match[1].strip()]

    def _process_collaboration_note_attachments(self, record, parsed_note: ParsedNote):
        """
        处理协作笔记的附件
        :param record: 笔记记录
        :param parsed_note: 解析后的笔记对象
        """
        # 从markdown内容中提取附件链接
        attachment_links = self._extract_attachment_links_from_markdown(parsed_note.content)
        if not attachment_links:
            return None

        try:
            token = self.api_client.get_collaboration_token(record['doc_guid'])
        except Exception as e:
            return f'协作笔记获取附件token失败: {type(e).__name__}: {e}'

        attachment_url_map = {}
        failures = []
        for attachment_name in attachment_links:
            label = f'{attachment_name} (doc_guid={record.get("doc_guid")})'
            try:
                attachment_byte = self._download_with_retry(
                    label,
                    lambda: self.api_client.get_collaboration_image_byte(token, record['doc_guid'], attachment_name),
                )
                FileManager.download_attachment_from_byte(record, attachment_name, attachment_byte)
                relative_path = f"./attachments/{attachment_name}"
                attachment_url_map[attachment_name] = relative_path
                log.info(f'协作笔记附件下载完成: {attachment_name}')
            except Exception as e:
                failures.append(f'{attachment_name}: {type(e).__name__}: {e}')
                log.warning(f'协作笔记附件下载失败(已重试): {attachment_name}, 错误: {type(e).__name__}: {e}')

        for original_name, local_path in attachment_url_map.items():
            parsed_note.content = parsed_note.content.replace(f'(wiz-collab-attachment://{original_name})', f'({local_path})')

        if failures:
            if len(failures) > 3:
                shown = failures[:3]
                return f'协作笔记附件下载失败: {"; ".join(shown)}; ...(+{len(failures) - 3} more)'
            return f'协作笔记附件下载失败: {"; ".join(failures)}'
        return None

    def _process_normal_note_attachments(self, record, parsed_note: ParsedNote):
        """
        处理普通笔记的附件
        :param record: 笔记记录
        :param parsed_note: 解析后的笔记对象
        """
        try:
            attachments = self.api_client.get_note_attachments(record['doc_guid'])
        except Exception as e:
            return f'普通笔记获取附件列表失败: {type(e).__name__}: {e}'

        if not attachments:
            return None

        attachment_list = []
        failures = []
        for attachment in attachments:
            att_guid = attachment.get('attGuid', 'unknown')
            att_name = attachment.get('name', 'unknown')
            label = f'{att_name} (att_guid={att_guid}, doc_guid={record.get("doc_guid")})'
            try:
                attachment_byte = self._download_with_retry(
                    label,
                    lambda: self.api_client.download_attachment(record['doc_guid'], att_guid, att_name=att_name),
                )
                FileManager.download_attachment_from_byte(record, att_name, attachment_byte)
                relative_path = f"./attachments/{att_name}"
                attachment_list.append(f"- [{att_name}]({relative_path})")
                log.info(f'普通笔记附件下载完成: {att_name}')
            except Exception as e:
                failures.append(f'{att_name}: {type(e).__name__}: {e}')
                log.warning(f'普通笔记附件下载失败(已重试): {att_name}, 错误: {type(e).__name__}: {e}')

        if attachment_list:
            attachment_section = "\n\n## 附件\n\n" + "\n".join(attachment_list) + "\n"
            parsed_note.content += attachment_section

        if failures:
            if len(failures) > 3:
                shown = failures[:3]
                return f'普通笔记附件下载失败: {"; ".join(shown)}; ...(+{len(failures) - 3} more)'
            return f'普通笔记附件下载失败: {"; ".join(failures)}'
        return None

    def _process_note_attachment(self, record, parsed_note: ParsedNote):
        # 判断笔记的类型
        if Note.is_collaboration_note(record['type']):
            return self._process_collaboration_note_attachments(record, parsed_note)
        else:
            return self._process_normal_note_attachments(record, parsed_note)

    # 将笔记和笔记图片写入图片, 并将图片上传到图床
    def _sync_note_to_local(self, unsync_records):
        for unsync_record in unsync_records:
            self._sync_single_note_to_local(unsync_record)

    def _sync_from_wiz_to_db(self):
        # 调用 wiz api 查询笔记总数
        wiz_note_count = self.api_client.get_note_count()
        # 调用 db 查询笔记同步记录总数
        db_note_count = self.db.get_note_count()
        log.info(f'wiz_note_count: {wiz_note_count}, db_note_count: {db_note_count}')

        # 如果两个个数不一致, 则说明有需要同步的笔记
        if wiz_note_count == db_note_count:
            return

        # 调用 wiz api 获取笔记列表
        wiz_note_list = self.api_client.get_note_list(0, self.PAGE_SIZE)
        # 如果一直不等于空集合
        while wiz_note_list:
            # 比较并获取待同步记录
            pending_sync_note_list = self.db.get_pending_sync_note_list(wiz_note_list)
            # 调用 db 插入待同步笔记记录
            self.db.insert_note_list(pending_sync_note_list)
            # 获取 wiz_note_list 中的最大 version
            max_version = NoteSynchronizer._get_max_version(wiz_note_list)
            log.info(f"max_version: {max_version}")
            wiz_note_list = self.api_client.get_note_list(max_version + 1, self.PAGE_SIZE)
        log.info('_sync_from_wiz_to_db end')

    @staticmethod
    def _get_max_version(note_list):
        # 如果集合空返回最大值 否则返回最大值
        return max([note['version'] for note in note_list]) if note_list else 999999999

    # 调用api, 根据笔记的类型获取笔记的原始内容, 入参笔记类型和doc_guid
    def _get_note_origin_content(self, note_type, doc_guid):
        if Note.is_collaboration_note(note_type):
            collaboration_token = self.api_client.get_collaboration_token(doc_guid)
            return self.api_client.get_collaboration_content(collaboration_token, doc_guid)
        detail = self.api_client.get_note_detail(doc_guid)
        return detail['html']
