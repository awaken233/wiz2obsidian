import json
import unittest
from sync.wiz_open_api import WizOpenApi
from log import log
from sync.note_parser_factory import NoteParserFactory
import re
from sync.note_property import NoteProperty
from sync.database import Database
from sync.note_synchronizer import NoteSynchronizer
from sync.config import Config


class TestNoteParserFactory(unittest.TestCase):

    def setUp(self):
        # 初始化WizOpenApi实例， 如果有初始化参数需要传入
        config = Config.load()
        self.wiz_open_api = WizOpenApi(config)

    # 测试解析html笔记的内容
    def test_parse_html_note(self):
        parser = NoteParserFactory.create_parser('document', 'html')
        doc_guid = 'bdfd068c-b12f-4ae4-ae68-8b6ba6e739ad'
        origin_content = self.wiz_open_api.get_note_detail(doc_guid)['html']
        log.info(f'原始内容: {origin_content}')
        parsed_note = parser.parse_content(origin_content)
        log.info(f'解析后的内容: {parsed_note}')


    # # 测试解析 lite 笔记的内容
    # def test_parse_lite_note(self):
    #     parser = NoteParserFactory.create_parser('lite/markdown')
    #     doc_guid = 'abe312a6-1ea6-4425-bacb-27da64eba993'
    #     origin_content = self.wiz_open_api.get_note_detail(doc_guid)['html']
    #     log.info(f'原始内容: {origin_content}')
    #     parsed_note = parser.parse_content(origin_content)
    #     log.info(f'解析后的内容: {parsed_note}')


    # # # 测试解析协作笔记的内容
    # def test_parse_collaboration_note(self):
    #     parser = NoteParserFactory.create_parser('collaboration')
    #     # 获取笔记的原始内容
    #     doc_guid = '8c049e78-ec9c-4cb7-8f98-d22416f02f5e'
    #     # doc_guid = 'dffe93ac-01d2-4add-8d12-ad0db0dc2188'
    #     collaboration_token = self.wiz_open_api.get_collaboration_token(doc_guid)
    #     origin_content = self.wiz_open_api.get_collaboration_content(collaboration_token, doc_guid)
    #     # 使用解析器解析笔记，将笔记转化为md, 并提取笔记中需要上传的图片
    #     parsed_note = parser.parse_content(origin_content)
    #     log.info(parsed_note)


    # 测试解析wss返回的内容
    # def test_parse_wss_content(self):
    #     parser = NoteParserFactory.create_parser('collaboration')
    #
    #     # 读取文件中的内容作为输入
    #     with open('test/wss.json', 'r') as f:
    #         origin_content = f.read()
    #
    #     # 使用解析器解析笔记，将笔记转化为md, 并提取笔记中需要上传的图片
    #     parsed_note = parser.parse_content(origin_content)
    #     log.info(parsed_note)
    #
    # def test_get_link_from_md(self):
    #     # 读取 Markdown 文件内容
    #     with open("test/co_md.md", "r") as file:
    #         markdown_text = file.read()
    #
    #     regex = r"!\[.*?\]\((.*?)\)"
    #     matches = re.findall(regex, markdown_text)
    #     log.info(matches)

    # 读取 html.md 文件中的内容, 去除多余的换行
    # def test_remove_extra_line(self):
    #     # 读取 Markdown 文件内容
    #     with open("test/html.md", "r") as file:
    #         markdown_text = file.read()
    #     # (?<!  \n)       : 负向后查找断言，匹配不是以两个空格和换行符结尾的行
    #     # (?<=.)(?<!  )\n : 行任意非换行字符结束，但不包括以两个空格结束的行
    #     # (?=\n|$)        : 前面 lookahead 断言，接下来是换行符或字符串结尾
    #     markdown_text = re.sub(r"(.*[^\s])\n((?:\n)+)", r"\1  \n", markdown_text)
    #     log.info(f'\n{markdown_text}')
    #     pyperclip.copy(markdown_text)


    # def test_property_to_string(self):
    #     with Database() as db:
    #         record = db.select_by_guid('dffe93ac-01d2-4add-8d12-ad0db0dc2188')
    #         sync_record = NoteProperty.from_sync_record(record)
    #         note_prop = sync_record.to_string()
    #         log.info(f'note_prop:\n{note_prop}')
    #
    #     np = NoteProperty(['category1', 'category2'], '2022-10-05 15:30:00', '2022-10-06 12:00:00', '中文')
    #     print(np.to_string())

    # # 测试同步指定笔记
    # def test_sync_note(self):
    #     with Database() as db:
    #         record = db.select_by_guid('1f570483-6266-4d7a-88df-b256f352da9e')
    #         syncer = NoteSynchronizer(self.wiz_open_api, db)
    #         syncer._sync_single_note_to_local(record)
