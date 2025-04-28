import os
import sys
from log import log

def init_output_dirs():
    """
    初始化程序所需的输出目录结构
    """
    # 获取应用程序的根目录路径
    if getattr(sys, "frozen", False):
        # 如果是打包后的可执行文件
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 需要创建的目录
    output_dirs = [
        os.path.join(application_path, 'output', 'db'),
        os.path.join(application_path, 'output', 'log'),
        os.path.join(application_path, 'output', 'note'),
    ]
    
    # 创建目录
    for dir_path in output_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            log.info(f"已创建目录: {dir_path}")
        except Exception as e:
            log.error(f"创建目录 {dir_path} 失败: {str(e)}")
            
    return application_path 