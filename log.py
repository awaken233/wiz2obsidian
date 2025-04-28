import logging.config
import logging.handlers
import yaml
import os
import sys
from datetime import datetime

# 获取配置文件和日志目录的基路径
if getattr(sys, "frozen", False):
    # 如果是打包后的可执行文件，基路径是 _MEIPASS 目录
    # sys.executable 是可执行文件本身的路径
    # sys._MEIPASS 是解压后的临时目录路径
    application_path = sys._MEIPASS
else:
    # 如果是开发环境，基路径是包含log.py的目录
    application_path = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
config_path = os.path.join(application_path, 'conf', 'logging.yaml')

# 日志文件输出目录 (相对于可执行文件或脚本运行目录)
# 保持日志输出在可执行文件旁边的output/log中，而不是_MEIPASS临时目录
if getattr(sys, "frozen", False):
    output_base_path = os.path.dirname(sys.executable)
else:
    output_base_path = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(output_base_path, 'output', 'log')
os.makedirs(log_dir, exist_ok=True)


# 加载日志配置
if not os.path.exists(config_path):
    # 如果在预期位置找不到配置文件，则抛出更明确的错误
    raise FileNotFoundError(f"Logging configuration file not found at expected path: {config_path}")

with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f.read())

# 更新日志文件路径为绝对路径
log_file = os.path.join(log_dir, f'log_{datetime.now().strftime("%Y-%m-%d")}.log')
config['handlers']['file']['filename'] = log_file

logging.config.dictConfig(config)

# 创建 log 对象
log = logging.getLogger()