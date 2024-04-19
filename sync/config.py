import yaml


class Config:
    CONFIG_FILE_PATH = "conf/conf.yaml"  # 配置文件路径

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password

    @classmethod
    def load(cls):
        with open(cls.CONFIG_FILE_PATH, "r") as file:
            config_data = yaml.safe_load(file)
            user_id = config_data["user_id"]
            password = config_data["password"]
            return cls(user_id, password)