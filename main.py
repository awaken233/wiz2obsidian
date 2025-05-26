from sync.note_synchronizer import NoteSynchronizer
from sync.database import Database
from sync.config import Config
from sync.wiz_open_api import WizOpenApi
from sync.init_dirs import init_output_dirs
from log import log
import unittest
from test.test_wiz_open_api import TestWizOpenApi
from test.test_note_parser_factory import TestNoteParserFactory
from test.test_note_synchronizer_integration import TestNoteSynchronizerIntegration
import os
import sys

def main():
    log.info("Start sync")
    
    # 初始化目录结构
    app_root = init_output_dirs()
    log.info(f"应用根目录: {app_root}")
    
    # 实例化配置管理器
    config = Config.load()

    # 实例化API客户端
    api_client = WizOpenApi(config)

    # 实例化数据库
    with Database() as db:
        db.init()
        # 实例化同步器
        synchronizer = NoteSynchronizer(api_client, db)

        # 执行同步笔记
        synchronizer.synchronize_notes()
    log.info("Sync finished")

def test_main():
    # 初始化目录结构
    init_output_dirs()
    
    # 创建一个测试加载器
    loader = unittest.TestLoader()

    # 创建一个测试套件
    suite = unittest.TestSuite()

    # 从指定的测试类中加载测试用例到测试套件
    # suite.addTest(loader.loadTestsFromTestCase(TestWizOpenApi))
    # suite.addTest(loader.loadTestsFromTestCase(TestNoteParserFactory))
    suite.addTest(loader.loadTestsFromTestCase(TestNoteSynchronizerIntegration))

    # 创建一个测试运行器
    runner = unittest.TextTestRunner()

    # 运行测试套件
    runner.run(suite)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_main()
    else:
        main()