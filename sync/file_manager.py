import os
from log import log
import requests


class FileManager:

    @staticmethod
    def _create_directory(directory_path):
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    def _write_file(directory_path, file_name, content):
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, "w") as file:
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
        # 当前脚本地址join output/note+category
        output_directory = os.path.join("output", "note", category.strip("/").replace("/", os.path.sep))
        FileManager._create_directory(output_directory)

        # 如果 title 是以 .md 结尾, 新文件的文件名无序添加 .md
        if title.endswith(".md"):
            title = title[:-3]

        FileManager._write_file(output_directory, title + '.md', content)

    # 保存图片到本地
    @staticmethod
    def save_image_to_file(category, title, file_name, content):
        output_directory = os.path.join("output", "export_image", category.strip("/").replace("/", os.path.sep), title)
        FileManager._create_directory(output_directory)
        FileManager._write_bfile(output_directory, file_name, content)

    @staticmethod
    def get_img_directory(record):
        """
        获取图片保存目录
        :param record:
        :return:
        """
        return os.path.join("output", "export_image", record['category'].strip("/").replace("/", os.path.sep), record['title'])

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
