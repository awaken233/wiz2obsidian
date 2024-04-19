import json
import yaml
import unittest
from sync.wiz_open_api import WizOpenApi
from log import log


class TestWizOpenApi(unittest.TestCase):

    def setUp(self):
        # 初始化WizOpenApi实例， 如果有初始化参数需要传入
        # 从配置文件 conf/conf.yaml 中读取配置
        with open('conf/conf.yaml', 'r') as f:
            config = yaml.safe_load(f.read())
        self.wiz_open_api = WizOpenApi(config['user_id'], config['password'])

    # def test_login_success(self):
    #     # 调用login方法并验证返回结果
    #     data = self.wiz_open_api.auth()
    #
    # def test_fetch_note_list_success(self):
    #     # 调用fetch_note_list方法并验证返回结果
    #     data = self.wiz_open_api.get_note_list(49439, 10)
    #     log.info(json.dumps(data))
    #
    # def test_get_note_detail_success(self):
    #     # html 笔记
    #     data = self.wiz_open_api.get_note_detail('e3459a11-c485-4b82-9fa2-402230d72c82')
    #     print('html 笔记', json.dumps(data))
    #     self.assertEqual(data['returnCode'], 200)
    #     # md 笔记(只有附件
    #     data = self.wiz_open_api.get_note_detail('d06918da-7042-46c9-8ed5-d8f52162ee12')
    #     print('md 笔记(只有附件', json.dumps(data))
    #     self.assertEqual(data['returnCode'], 200)
    #     # md 笔记(只有图片
    #     data = self.wiz_open_api.get_note_detail('f4b1c6b6-ba35-4893-ad97-7d5018f26733')
    #     print('md 笔记(只有图片', json.dumps(data))
    #     self.assertEqual(data['returnCode'], 200)
    #
    # def test_get_collaboration_token(self):
    #     self.wiz_open_api.auth()
    #     data = self.wiz_open_api.get_collaboration_token('dffe93ac-01d2-4add-8d12-ad0db0dc2188')
    #     log.info(data)
    #
    # def test_get_collaboration_content(self):
    #     token = self.wiz_open_api.get_collaboration_token('dffe93ac-01d2-4add-8d12-ad0db0dc2188')
    #     content = self.wiz_open_api.get_collaboration_content(token, 'dffe93ac-01d2-4add-8d12-ad0db0dc2188')
    #     log.info(f'wss return data: {content}')
    #
    # def test_get_collaboration_image_byte(self):
    #     self.wiz_open_api.auth()
    #     token = self.wiz_open_api.get_collaboration_token('dffe93ac-01d2-4add-8d12-ad0db0dc2188')
    #     image_byte = self.wiz_open_api.get_collaboration_image_byte(token, 'dffe93ac-01d2-4add-8d12-ad0db0dc2188', 'cXuKjvSNNxWugTRtjQUHUNSv1sLxm8ed3bleFBLz7-E.png')
    #     # 将文件保存到本地
    #     with open('output/export_image/cXuKjvSNNxWugTRtjQUHUNSv1sLxm8ed3bleFBLz7-E.png', 'wb') as f:
    #         f.write(image_byte)
    #

    # def test_upgrade_note(self):
    #     data = self.wiz_open_api.upgrade_note('03d697c7-2e94-474b-96cd-d45b0af796f5')
    #     log.info(data)

    # def test_download_note(self):
    #     data = self.wiz_open_api.get_note_detail('03d697c7-2e94-474b-96cd-d45b0af796f5')
    #     log.info(f'download_note: {json.dumps(data)}')



