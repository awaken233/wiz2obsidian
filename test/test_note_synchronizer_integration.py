import json
import unittest
import os
import tempfile
import shutil
from sync.file_manager import FileManager
from sync.wiz_open_api import WizOpenApi
from log import log
from sync.note_synchronizer import NoteSynchronizer
from sync.database import Database
from sync.config import Config
from sync.init_dirs import init_output_dirs


class TestNoteSynchronizerIntegration(unittest.TestCase):
    """
    NoteSynchronizer._sync_single_note_to_local 方法的集成测试
    测试协作笔记和普通笔记的完整同步流程
    """

    def setUp(self):
        """初始化测试环境"""
        # 初始化目录结构
        init_output_dirs()
        
        # 初始化配置和API客户端
        config = Config.load()
        self.wiz_open_api = WizOpenApi(config)
        
        # 初始化数据库
        self.db = Database()
        self.db.__enter__()
        self.db.init()
        
        # 初始化同步器
        self.synchronizer = NoteSynchronizer(self.wiz_open_api, self.db)
        
        # 测试用笔记ID
        self.collaboration_note_guid = 'dffe93ac-01d2-4add-8d12-ad0db0dc2188'  # 协作笔记
        self.normal_note_guid = 'd06918da-7042-46c9-8ed5-d8f52162ee12'        # 普通笔记

    def tearDown(self):
        """清理测试环境"""
        # 关闭数据库连接
        self.db.__exit__(None, None, None)

    def _get_test_record_from_db(self, doc_guid):
        """
        从数据库查询真实的笔记记录
        """
        try:
            record = self.db.select_by_guid(doc_guid)
            log.info(f"从数据库获取记录: {record['title']} (类型: {record['type']})")
            return record
        except (IndexError, Exception) as e:
            self.skipTest(f"测试笔记记录不存在于数据库中: {doc_guid}. 请先运行完整同步或手动添加测试记录。错误: {str(e)}")

    def test_sync_collaboration_note_integration(self):
        """
        测试协作笔记的完整同步流程
        """
        log.info("开始测试协作笔记集成同步")
        
        # 从数据库查询真实的测试记录
        test_record = self._get_test_record_from_db(self.collaboration_note_guid)
        
        try:
            # 执行同步
            self.synchronizer._sync_single_note_to_local(test_record)
            
            # 验证同步结果
            self._verify_sync_result(test_record, is_collaboration=True)
            
            log.info("协作笔记集成测试完成")
        except Exception as e:
            self.fail(f"协作笔记同步失败: {str(e)}")

    def test_sync_normal_note_integration(self):
        """
        测试普通笔记的完整同步流程
        """
        log.info("开始测试普通笔记集成同步")
        
        # 从数据库查询真实的测试记录
        test_record = self._get_test_record_from_db(self.normal_note_guid)
        
        try:
            # 执行同步
            self.synchronizer._sync_single_note_to_local(test_record)
            
            # 验证同步结果
            self._verify_sync_result(test_record, is_collaboration=False)
            
            log.info("普通笔记集成测试完成")
        except Exception as e:
            self.fail(f"普通笔记同步失败: {str(e)}")

    def _verify_sync_result(self, test_record, is_collaboration):
        """
        验证同步结果
        """
        # 检查文件是否生成
        app_root = FileManager.get_app_root()
        note_file_path = os.path.join(
            app_root, 
            "output", 
            "note", 
            test_record['category'].strip("/"), 
            test_record['title'] + '.md'
        )
        
        self.assertTrue(os.path.exists(note_file_path), f"笔记文件未生成: {note_file_path}")
        
        # 检查文件内容
        with open(note_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证文件包含YAML前置元数据
        self.assertTrue(content.startswith('---'), "文件应包含YAML前置元数据")
        self.assertIn('CREATE_TIME:', content, "文件应包含创建时间")
        self.assertIn('UPDATE_TIME:', content, "文件应包含更新时间")
        self.assertIn('tags:', content, "文件应包含标签")
        
        # 验证笔记内容不为空
        yaml_end = content.find('---', 3)  # 找到第二个 ---
        if yaml_end != -1:
            note_content = content[yaml_end + 3:].strip()
            self.assertTrue(len(note_content) > 0, "笔记内容不应为空")
        
        log.info(f"{'协作' if is_collaboration else '普通'}笔记同步验证通过")

if __name__ == '__main__':
    unittest.main() 