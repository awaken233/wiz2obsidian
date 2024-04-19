from datetime import datetime
import yaml


# 笔记属性
class NoteProperty:
    def __init__(self, category, created, accessed, url):
        self.CREATE_TIME = created
        self.UPDATE_TIME = accessed
        self.tags = category
        self.url = url

    @classmethod
    def from_sync_record(cls, record):
        """
        从同步记录生成笔记属性
        :param record: 上传记录
        :return:
        """
        # 解析category字段为list
        category = record['category'].strip('/').split('/')
        # 时间戳转换为日期格式
        created = cls.timestamp_to_date(record['created'])
        accessed = cls.timestamp_to_date(record['accessed'])
        url = record.get('url', '') or ''
        return cls(category, created, accessed, url)

    def to_string(self):
        """
        将 ObProperty 对象转换为ob需要的 YAML 字符串
        :return:
        """
        yaml_str = yaml.safe_dump(self.__dict__, allow_unicode=True)
        # 序列化日期会默认带上单引号, 但是obsidian 是不带单引号的, 所以需要去除日期值的单引号
        yaml_str = yaml_str.replace("'", "")
        return f'---\n{yaml_str}---\n'


    @classmethod
    def timestamp_to_date(cls, timestamp):
        # 假设timestamp是毫秒格式
        return datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

