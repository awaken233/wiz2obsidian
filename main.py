from sync.note_synchronizer import NoteSynchronizer
from sync.database import Database
from sync.config import Config
from sync.wiz_open_api import WizOpenApi
from log import log
import unittest
from test.test_wiz_open_api import TestWizOpenApi
from test.test_note_parser_factory import TestNoteParserFactory

def main():
    log.info("Start sync")
    # 实例化配置管理器
    config = Config.load()

    # 实例化API客户端
    api_client = WizOpenApi(config.user_id, config.password)

    # 实例化数据库
    with Database() as db:
        db.init()
        # 实例化同步器
        synchronizer = NoteSynchronizer(api_client, db)

        # 执行同步笔记
        synchronizer.synchronize_notes()
    log.info("Sync finished")

def test_main():
    unittest.main(module=TestWizOpenApi.__module__, exit=False)
    unittest.main(module=TestNoteParserFactory.__module__, exit=False)


if __name__ == "__main__":
    main()
    # test_main()