import logging.config
import yaml
import os

# 加载配置文件
# current_dir = os.path.dirname(os.path.abspath(__file__))
# log_config_path = os.path.join(current_dir, 'conf', 'logging.yaml')

with open('conf/logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)

# 创建 log 对象
log = logging.getLogger(__name__)