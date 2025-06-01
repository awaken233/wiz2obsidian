import os
import sys
from log import log
import requests


class FileManager:
    # 应用程序根目录缓存
    _app_root = None

    @staticmethod
    def get_app_root():
        """获取应用程序根目录"""
        if FileManager._app_root is None:
            if getattr(sys, "frozen", False):
                # 如果是打包后的可执行文件
                FileManager._app_root = os.path.dirname(sys.executable)
            else:
                # 如果是开发环境
                FileManager._app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return FileManager._app_root

    @staticmethod
    def _create_directory(directory_path):
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    def _write_file(directory_path, file_name, content):
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def _write_bfile(directory_path, file_name, content):
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, "wb") as file:
            file.write(content)

    @staticmethod
    def save_md_to_file(category, title, content):
        """
        保存md文件
        :param category:  笔记的目录 eg: /xx1/xx2/
        :param title: 笔记标题
        :param content:
        :return:
        """
        # 使用绝对路径
        app_root = FileManager.get_app_root()
        output_directory = os.path.join(app_root, "output", "note", category.strip("/").replace("/", os.path.sep))
        FileManager._create_directory(output_directory)

        # 清理 title，防止包含路径分隔符
        safe_title = title.replace("/", "_").replace("\\", "_")
        if safe_title.endswith(".md"):
            safe_title = safe_title[:-3]

        FileManager._write_file(output_directory, safe_title + '.md', content)

    # 保存图片到本地
    @staticmethod
    def save_image_to_file(category, title, file_name, content):
        app_root = FileManager.get_app_root()
        output_directory = os.path.join(app_root, "output", "export_image", category.strip("/").replace("/", os.path.sep), title)
        FileManager._create_directory(output_directory)
        FileManager._write_bfile(output_directory, file_name, content)

    @staticmethod
    def get_img_directory(record):
        """
        获取图片保存目录: 当前笔记同级目录下 ./images/
        :param record: 笔记同步记录
        :return:
        """
        app_root = FileManager.get_app_root()
        return os.path.join(app_root, "output", "note", record['category'].strip("/").replace("/", os.path.sep), "images")

    @staticmethod
    def get_attachments_directory(record):
        """
        获取附件保存目录: 当前笔记同级目录下 ./attachments/
        :param record: 笔记同步记录
        :return:
        """
        app_root = FileManager.get_app_root()
        return os.path.join(app_root, "output", "note", record['category'].strip("/").replace("/", os.path.sep), "attachments")

    @staticmethod
    def image_file_is_not_exist(record, img_file_name):
        img_directory = FileManager.get_img_directory(record)
        full_path = os.path.join(img_directory, img_file_name)
        return not os.path.exists(full_path)

    @staticmethod
    def download_img_from_url(record, img_file_name, url):
        img_directory = FileManager.get_img_directory(record)
        FileManager._create_directory(img_directory)
        full_path = os.path.join(img_directory, img_file_name)
        log.info(f"download_img_from_url {full_path}")

        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        with open(full_path, 'wb') as file:
            file.write(response.content)
        log.info(f"文件下载完成 {img_file_name}")

    @staticmethod
    def download_img_from_byte(record, img_file_name, byte):
        img_directory = FileManager.get_img_directory(record)
        FileManager._create_directory(img_directory)
        full_path = os.path.join(img_directory, img_file_name)
        log.info(f"download_img_from_byte {full_path}")
        with open(full_path, "wb") as file:
            file.write(byte)

    @staticmethod
    def download_attachment_from_byte(record, att_file_name, byte_content):
        """
        从二进制内容下载附件到本地
        :param record: 笔记同步记录
        :param att_file_name: 附件文件名
        :param byte_content: 附件二进制内容
        :return:
        """
        attachments_directory = FileManager.get_attachments_directory(record)
        FileManager._create_directory(attachments_directory)
        full_path = os.path.join(attachments_directory, att_file_name)
        log.info(f"download_attachment_from_byte {full_path}")
        with open(full_path, "wb") as file:
            file.write(byte_content)


    @staticmethod
    def get_not_in_local_img(record, need_upload_images):
        """
        获取本地资源管理器不存在的图片
        :param record: 上传记录
        :param need_upload_images: 需要上传图片的文件名
        :return: 本地不存在的文件名
        """
        # 如果需要上传图片的集合为空, 直接返回空dict
        if not need_upload_images:
            return {}

        # 判断哪些图片文件没有保存到本地
        not_in_local_img = list(filter(lambda x: FileManager.image_file_is_not_exist(record, x), need_upload_images))
        log.info(f'not_in_local_img: {not_in_local_img} need_upload_images: {need_upload_images}')
        return not_in_local_img
