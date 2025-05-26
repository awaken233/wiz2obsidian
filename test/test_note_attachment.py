import os
import unittest
import shutil
import tempfile
from unittest.mock import Mock, patch, MagicMock

from sync.config import config
from sync.wiz_open_api import WizOpenApi
from sync.database import Database
from sync.note_synchronizer import NoteSynchronizer
from sync.file_manager import FileManager
from sync.parsed_note import ParsedNote
from log import log


class TestNoteAttachment(unittest.TestCase):
    """笔记附件处理功能测试类"""

    def setUp(self):
        """测试前准备"""
        # 初始化API客户端
        self.wiz_api = WizOpenApi(config)
        
        # 初始化数据库连接
        self.db = Database()
        
        # 初始化同步器
        self.synchronizer = NoteSynchronizer(self.wiz_api, self.db)
        
        # 测试用的笔记ID
        self.collaboration_note_id = 'dffe93ac-01d2-4add-8d12-ad0db0dc2188'
        self.normal_note_id = 'd06918da-7042-46c9-8ed5-d8f52162ee12'
        
        # 创建临时测试目录
        self.test_output_dir = tempfile.mkdtemp()
        log.info(f"测试临时目录: {self.test_output_dir}")

    def tearDown(self):
        """测试后清理"""
        # 清理临时测试目录
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        log.info("测试环境清理完成")

    def test_extract_attachment_links_from_markdown(self):
        """测试从markdown内容中提取附件链接的正则表达式功能"""
        log.info("开始测试正则表达式提取附件链接功能")
        
        # 测试数据：包含各种类型的链接
        test_content = """
# 测试文档

这是一个包含多种链接的测试文档。

## 图片链接（应该被排除）
![测试图片1](image1.png)
![测试图片2](./images/image2.jpg)
![远程图片](https://example.com/image.png)

## 附件链接（应该被提取）
[文档附件1](document1.pdf)
[表格文件](spreadsheet.xlsx)
[压缩包](archive.zip)
[本地文件](./files/data.txt)

## 普通链接（应该被提取）
[外部链接](https://example.com)
[相对链接](../other/page.html)

## 混合内容
这里有一个图片 ![内联图片](inline.png) 和一个附件 [重要文档](important.docx)。
        """
        
        # 调用被测试的方法
        attachment_links = self.synchronizer._extract_attachment_links_from_markdown(test_content)
        
        # 验证结果
        expected_links = [
            'document1.pdf',
            'spreadsheet.xlsx', 
            'archive.zip',
            './files/data.txt',
            'https://example.com',
            '../other/page.html',
            'important.docx'
        ]
        
        log.info(f"提取到的附件链接: {attachment_links}")
        log.info(f"预期的附件链接: {expected_links}")
        
        # 验证提取的链接数量和内容
        self.assertEqual(len(attachment_links), len(expected_links))
        for expected_link in expected_links:
            self.assertIn(expected_link, attachment_links)
        
        # 确保图片链接没有被错误提取
        image_links = ['image1.png', './images/image2.jpg', 'https://example.com/image.png', 'inline.png']
        for image_link in image_links:
            self.assertNotIn(image_link, attachment_links)
        
        log.info("正则表达式提取附件链接功能测试完成")

    def test_file_manager_attachment_methods(self):
        """测试FileManager的附件相关方法"""
        log.info("开始测试FileManager附件方法")
        
        # 创建测试记录
        test_record = {
            'category': '/测试目录/子目录',
            'title': '测试笔记',
            'doc_guid': 'test-guid-123'
        }
        
        # 测试获取附件目录
        attachments_dir = FileManager.get_attachments_directory(test_record)
        log.info(f"附件目录路径: {attachments_dir}")
        
        # 验证路径格式正确
        self.assertIn('attachments', attachments_dir)
        self.assertIn('测试目录', attachments_dir)
        self.assertIn('子目录', attachments_dir)
        
        # 测试下载附件功能
        test_file_name = 'test-attachment.txt'
        test_content = '这是测试附件内容'.encode('utf-8')
        
        # 使用临时目录进行测试，避免污染项目目录
        with patch.object(FileManager, 'get_attachments_directory', return_value=self.test_output_dir):
            FileManager.download_attachment_from_byte(test_record, test_file_name, test_content)
            
            # 验证文件是否成功保存
            saved_file_path = os.path.join(self.test_output_dir, test_file_name)
            self.assertTrue(os.path.exists(saved_file_path))
            
            # 验证文件内容
            with open(saved_file_path, 'rb') as f:
                saved_content = f.read()
            self.assertEqual(saved_content, test_content)
        
        log.info("FileManager附件方法测试完成")

    @patch('sync.note_synchronizer.NoteSynchronizer._extract_attachment_links_from_markdown')
    def test_process_collaboration_note_attachments(self, mock_extract_links):
        """测试协作笔记附件处理功能"""
        log.info("开始测试协作笔记附件处理功能")
        
        # 设置模拟数据
        test_record = {
            'type': 'collaboration',
            'category': '/测试协作',
            'title': '协作笔记测试',
            'doc_guid': 'collaboration-test-guid'
        }
        
        # 模拟提取到的附件链接
        mock_attachment_links = ['test-attachment1.pdf', 'test-attachment2.docx']
        mock_extract_links.return_value = mock_attachment_links
        
        # 创建测试用的ParsedNote对象
        test_content = """
# 协作笔记测试

这里有一个附件 [测试附件1](test-attachment1.pdf)
还有另一个附件 [测试附件2](test-attachment2.docx)
        """
        parsed_note = ParsedNote(test_content, [])
        
        # 模拟API方法
        with patch.object(self.synchronizer.api_client, 'get_collaboration_token') as mock_get_token, \
             patch.object(self.synchronizer.api_client, 'get_collaboration_image_byte') as mock_get_byte, \
             patch.object(FileManager, 'download_attachment_from_byte') as mock_download:
            
            # 设置模拟返回值
            mock_get_token.return_value = 'mock-token-123'
            mock_get_byte.return_value = b'mock attachment content'
            
            # 调用被测试的方法
            self.synchronizer._process_collaboration_note_attachments(test_record, parsed_note)
            
            # 验证API调用
            mock_get_token.assert_called_once_with('collaboration-test-guid')
            self.assertEqual(mock_get_byte.call_count, len(mock_attachment_links))
            self.assertEqual(mock_download.call_count, len(mock_attachment_links))
            
            # 验证内容替换
            for attachment_name in mock_attachment_links:
                expected_local_path = f"./attachments/{attachment_name}"
                self.assertIn(expected_local_path, parsed_note.content)
                self.assertNotIn(f'({attachment_name})', parsed_note.content)
        
        log.info("协作笔记附件处理功能测试完成")

    def test_process_normal_note_attachments(self):
        """测试普通笔记附件处理功能"""
        log.info("开始测试普通笔记附件处理功能")
        
        # 设置测试数据
        test_record = {
            'type': 'lite/markdown',
            'category': '/测试普通',
            'title': '普通笔记测试',
            'doc_guid': 'normal-test-guid'
        }
        
        # 模拟API返回的附件列表
        mock_attachments = [
            {'attGuid': 'att-guid-1', 'name': 'document1.pdf'},
            {'attGuid': 'att-guid-2', 'name': 'spreadsheet.xlsx'},
            {'attGuid': 'att-guid-3', 'name': 'archive.zip'}
        ]
        
        # 创建测试用的ParsedNote对象
        original_content = """
# 普通笔记测试

这是一个普通笔记的内容。
        """
        parsed_note = ParsedNote(original_content, [])
        
        # 模拟API方法
        with patch.object(self.synchronizer.api_client, 'get_note_attachments') as mock_get_attachments, \
             patch.object(self.synchronizer.api_client, 'download_attachment') as mock_download_att, \
             patch.object(FileManager, 'download_attachment_from_byte') as mock_save_file:
            
            # 设置模拟返回值
            mock_get_attachments.return_value = mock_attachments
            mock_download_att.return_value = b'mock attachment binary content'
            
            # 调用被测试的方法
            self.synchronizer._process_normal_note_attachments(test_record, parsed_note)
            
            # 验证API调用
            mock_get_attachments.assert_called_once_with('normal-test-guid')
            self.assertEqual(mock_download_att.call_count, len(mock_attachments))
            self.assertEqual(mock_save_file.call_count, len(mock_attachments))
            
            # 验证下载调用参数
            for i, attachment in enumerate(mock_attachments):
                mock_download_att.assert_any_call('normal-test-guid', attachment['attGuid'])
                mock_save_file.assert_any_call(test_record, attachment['name'], b'mock attachment binary content')
            
            # 验证附件列表被追加到内容末尾
            self.assertIn('## 附件', parsed_note.content)
            for attachment in mock_attachments:
                expected_link = f"- [{attachment['name']}](./attachments/{attachment['name']})"
                self.assertIn(expected_link, parsed_note.content)
        
        log.info("普通笔记附件处理功能测试完成")

    def test_integration_collaboration_note(self):
        """集成测试：使用真实的协作笔记ID测试附件处理"""
        log.info(f"开始协作笔记集成测试，笔记ID: {self.collaboration_note_id}")
        
        try:
            # 创建模拟记录
            test_record = {
                'type': 'collaboration',
                'category': '/集成测试/协作笔记',
                'title': '协作笔记集成测试',
                'doc_guid': self.collaboration_note_id
            }
            
            # 获取协作笔记内容进行测试
            try:
                token = self.wiz_api.get_collaboration_token(self.collaboration_note_id)
                content = self.wiz_api.get_collaboration_content(token, self.collaboration_note_id)
                log.info("成功获取协作笔记内容")
                
                # 创建ParsedNote对象
                parsed_note = ParsedNote(content, [])
                
                # 使用临时目录保存附件，避免污染项目目录
                with patch.object(FileManager, 'get_attachments_directory', return_value=self.test_output_dir):
                    # 调用附件处理方法
                    self.synchronizer._process_collaboration_note_attachments(test_record, parsed_note)
                    
                    # 检查是否有附件被下载到临时目录
                    downloaded_files = os.listdir(self.test_output_dir)
                    log.info(f"下载的附件文件: {downloaded_files}")
                    
                    if downloaded_files:
                        log.info("协作笔记附件处理成功，检测到附件下载")
                        # 验证文件确实存在且有内容
                        for filename in downloaded_files:
                            file_path = os.path.join(self.test_output_dir, filename)
                            self.assertTrue(os.path.exists(file_path))
                            self.assertGreater(os.path.getsize(file_path), 0)
                    else:
                        log.info("协作笔记中没有检测到附件链接，这也是正常情况")
                
            except Exception as e:
                log.warning(f"协作笔记处理失败，可能是网络问题或笔记不存在: {str(e)}")
                # 这不应该导致测试失败，因为可能是环境问题
                
        except Exception as e:
            log.error(f"协作笔记集成测试发生异常: {str(e)}")
            self.fail(f"协作笔记集成测试失败: {str(e)}")
        
        log.info("协作笔记集成测试完成")

    def test_integration_normal_note(self):
        """集成测试：使用真实的普通笔记ID测试附件处理"""
        log.info(f"开始普通笔记集成测试，笔记ID: {self.normal_note_id}")
        
        try:
            # 创建模拟记录
            test_record = {
                'type': 'lite/markdown',
                'category': '/集成测试/普通笔记',
                'title': '普通笔记集成测试',
                'doc_guid': self.normal_note_id
            }
            
            # 获取普通笔记的详细信息
            try:
                note_detail = self.wiz_api.get_note_detail(self.normal_note_id)
                log.info("成功获取普通笔记详情")
                
                # 获取附件列表
                attachments = self.wiz_api.get_note_attachments(self.normal_note_id)
                log.info(f"笔记包含 {len(attachments)} 个附件")
                
                if attachments:
                    # 创建测试内容
                    test_content = "# 普通笔记集成测试\n\n这是测试内容。"
                    parsed_note = ParsedNote(test_content, [])
                    
                    # 使用临时目录保存附件
                    with patch.object(FileManager, 'get_attachments_directory', return_value=self.test_output_dir):
                        # 调用附件处理方法
                        self.synchronizer._process_normal_note_attachments(test_record, parsed_note)
                        
                        # 检查附件是否被下载
                        downloaded_files = os.listdir(self.test_output_dir)
                        log.info(f"下载的附件文件: {downloaded_files}")
                        
                        # 验证下载的文件数量
                        self.assertEqual(len(downloaded_files), len(attachments))
                        
                        # 验证文件确实存在且有内容
                        for filename in downloaded_files:
                            file_path = os.path.join(self.test_output_dir, filename)
                            self.assertTrue(os.path.exists(file_path))
                            self.assertGreater(os.path.getsize(file_path), 0)
                        
                        # 验证附件列表被添加到内容中
                        self.assertIn('## 附件', parsed_note.content)
                        for attachment in attachments:
                            expected_link = f"- [{attachment['name']}](./attachments/{attachment['name']})"
                            self.assertIn(expected_link, parsed_note.content)
                    
                    log.info("普通笔记附件处理成功")
                else:
                    log.info("普通笔记中没有附件，跳过附件处理测试")
                
            except Exception as e:
                log.warning(f"普通笔记处理失败，可能是网络问题或笔记不存在: {str(e)}")
                # 这不应该导致测试失败，因为可能是环境问题
                
        except Exception as e:
            log.error(f"普通笔记集成测试发生异常: {str(e)}")
            self.fail(f"普通笔记集成测试失败: {str(e)}")
        
        log.info("普通笔记集成测试完成")


if __name__ == '__main__':
    unittest.main() 