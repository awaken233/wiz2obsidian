import os
import sys

from dotenv import load_dotenv # 导入 os
from log import log

# 获取应用程序的根目录路径
if getattr(sys, "frozen", False):
    # 如果是打包后的可执行文件
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是开发环境
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 指定 .env 文件的路径
dotenv_path = os.path.join(application_path, ".env")

if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"环境变量文件 {dotenv_path} 不存在")

log.info(f"环境变量文件路径: {dotenv_path}")
load_dotenv(dotenv_path)

class Config:

    def __init__(self, user_id, password, group_name):
        self.user_id = user_id
        self.password = password
        self.group_name = group_name

    @classmethod
    def load(cls):
        # 从环境变量读取配置
        user_id = os.getenv("WIZ_USER_ID")
        password = os.getenv("WIZ_PASSWORD")
        group_name = os.getenv("WIZ_GROUP_NAME")

        if not user_id or not password:
            raise ValueError("请在 .env 文件中设置 WIZ_USER_ID 和 WIZ_PASSWORD")
        
        # group_name 是可选的
        return cls(user_id, password, group_name if group_name else "")