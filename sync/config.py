import os # 导入 os
from dotenv import load_dotenv # 导入 load_dotenv

load_dotenv() # 加载 .env 文件

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