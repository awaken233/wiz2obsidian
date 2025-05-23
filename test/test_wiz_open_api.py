import json
import unittest
import os
from sync.wiz_open_api import WizOpenApi
from sync.config import config
from log import log


class TestWizOpenApi(unittest.TestCase):

    def setUp(self):
        self.wiz_open_api = WizOpenApi(config)

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

    # def test_get_note_attachments(self):
    #     """测试获取笔记附件列表"""
    #     doc_guid = 'd06918da-7042-46c9-8ed5-d8f52162ee12'
    #     attachments = self.wiz_open_api.get_note_attachments(doc_guid)
    #     log.info(f'获取到的附件列表: {json.dumps(attachments, ensure_ascii=False, indent=2)}')
        
    #     # 基础验证
    #     self.assertIsNotNone(attachments)
    #     self.assertIsInstance(attachments, list)
    #     log.info(f'附件数量: {len(attachments)}')
        
    #     for i, attachment in enumerate(attachments):
    #         log.info(f'附件 {i+1}: 名称={attachment.get("name")}, attGuid={attachment.get("attGuid")}')

    # def test_download_attachment(self):
    #     """测试下载笔记附件"""
    #     doc_guid = 'd06918da-7042-46c9-8ed5-d8f52162ee12'
        
    #     # 首先获取附件列表
    #     attachments = self.wiz_open_api.get_note_attachments(doc_guid)
    #     log.info(f'获取到 {len(attachments)} 个附件')
        
    #     # 验证有附件可供下载
    #     self.assertGreater(len(attachments), 0, '测试笔记应该包含至少一个附件')
        
    #     # 选择第一个附件进行下载测试
    #     first_attachment = attachments[0]
    #     att_guid = first_attachment['attGuid']
    #     file_name = first_attachment['name']
        
    #     log.info(f'开始下载附件: {file_name} (GUID: {att_guid})')
        
    #     # 下载附件
    #     attachment_content = self.wiz_open_api.download_attachment(doc_guid, att_guid)
        
    #     # 验证下载内容
    #     self.assertIsNotNone(attachment_content)
    #     self.assertIsInstance(attachment_content, bytes)
        
    #     log.info(f'附件下载成功，大小: {len(attachment_content)} bytes')
        
    #     # 创建输出目录并保存文件
    #     output_dir = 'output/test_attachments'
    #     os.makedirs(output_dir, exist_ok=True)
        
    #     file_path = os.path.join(output_dir, file_name)
    #     with open(file_path, 'wb') as f:
    #         f.write(attachment_content)
        
    #     log.info(f'附件已保存到: {file_path}')
        
    #     # 验证文件保存成功
    #     self.assertTrue(os.path.exists(file_path))



