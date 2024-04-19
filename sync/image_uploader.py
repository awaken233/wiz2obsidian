import sys
from log import log
from sync.file_manager import FileManager

import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 使用 picgo http api 上传图片.


class ImageUploader:
    UPLOAD_URL = 'http://127.0.0.1:36677/upload'

    def __init__(self):
        # 创建Session对象
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        # 设置请求超时
        self.timeout = 5  # 秒


    def upload(self, record, image_name):
        log.info(f"开始上传图片 {record} {image_name}")

        file_path = FileManager.get_img_directory(record)
        log.info(f'笔记对应的图片目录为: {file_path}')

        # 获取图片的全路径
        image_full_path = os.path.join(file_path, image_name)
        # 获取当前文件的绝对路径
        image_full_path = os.path.join(os.getcwd(), image_full_path)
        log.info(f'图片全路径为: {image_full_path}')


        # 调用上传接口
        try:
            resp = self.session.post(url=ImageUploader.UPLOAD_URL, json={'list': [image_full_path]})
        except requests.exceptions.RequestException as e:
            log.info(f"连接异常, 请检查picgo是否启动, 错误信息: {str(e)}")
            sys.exit(1)
        log.info(resp.text)

        # 成功和失败的返回值
        # {"success":true,"result":["图片地址1", "图片地址2"]}
        # {"success":false,"message":"upload error. see /Users/ve/Library/Application Support/picgo/picgo.log for more detail."}
        if resp.json()['success'] == True:
            log.info(f"上传成功 {image_name}")
            # 获取上传成功后的图片地址
            image_url = resp.json()['result'][0]
            return image_url
        else:
            log.info(f"上传失败 {image_name}")
            raise Exception(f"上传失败 {image_name} {resp.json()['message']}")
        # return 'https://cdn.jsdelivr.net/gh/awaken233/Graphicbed/ys1/53418722-6822-40e1-8747-7c1712026a7b.png'


