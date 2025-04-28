import logging.config
import logging.handlers
import yaml
import os
import sys
from datetime import datetime

# 获取应用程序的根目录路径
if getattr(sys, "frozen", False):
    # 如果是打包后的可执行文件
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是开发环境
    application_path = os.path.dirname(os.path.abspath(__file__))

# 确保日志目录存在
log_dir = os.path.join(application_path, 'output', 'log')
os.makedirs(log_dir, exist_ok=True)

# 加载配置文件路径
config_path = os.path.join(application_path, 'conf', 'logging.yaml')
if not os.path.exists(config_path):
    # 如果打包环境下找不到配置文件，尝试使用相对路径
    config_path = 'conf/logging.yaml'

with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f.read())

# 更新日志文件路径为绝对路径
log_file = os.path.join(log_dir, f'log_{datetime.now().strftime("%Y-%m-%d")}.log')
config['handlers']['file']['filename'] = log_file

logging.config.dictConfig(config)

# 创建 log 对象
log = logging.getLogger()