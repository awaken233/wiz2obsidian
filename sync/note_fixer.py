from log import log
import re


HEADING_PATTERN = re.compile(r'^(#{1,6})(?!\s+)(\w+)')


def fix_markdown_title(content):
    """
    修复标题#后面可能没有空格,格式不规范的问题
    :param content:
    :return: 返回修复后文本
    """
    lines = content.split('\n')
    output_lines = []
    for line in lines:
        output_lines.append(fix_markdown_title_line_by_line(line))
    return '\n'.join(output_lines)

def fix_markdown_title_line_by_line(line):
    """
    修复标题#后面可能没有空格,格式不规范的问题
    :param line:
    :return: 返回修复后文本行
    """
    if not line.startswith('#'):
        return line

    # 如果匹配返回修正后的字符串
    if HEADING_PATTERN.match(line):
        result = re.sub(HEADING_PATTERN, r'\1 \2', line)
        return result
    return line


CODE_BLOCK_PATTERN = re.compile(r'^```.*?```', re.DOTALL)


def fix_markdown_code_block(content):
    """
    修复代码块多余的空行
    :param content:
    :return: 返回修复后文本
    """
    # 按回车符分隔 content
    # 判断当前行是否以 ``` 开头, 如果是, 代码块开始, 开始计数, 忽略代码块开始的奇数行
    # 判断当前行是否一 ``` 开头, 如果是, 代码块结束, 重置计数

    line_num = 0
    code_block = False
    fix_content = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith('```'):
            code_block = not code_block
            line_num = 0
        if code_block:
            line_num+=1
            if line_num % 2 == 0:
                if line.isspace() or len(line) == 0:
                    continue
                else:
                    line_num+=1
        fix_content.append(line)
    return '\n'.join(fix_content)

def fix_markdown_list(content):
    """
    使用正则将文本中的所有 \- 开头的文字替换为 -
    :param content:
    :return:
    """
    return content.replace('\- ', '- ')


class NoteFixer:

    @staticmethod
    def fix(markdown_content):
        # 一些后置处理
        file_content = fix_markdown_title(markdown_content)
        file_content = fix_markdown_code_block(file_content)
        file_content = fix_markdown_list(file_content)
        # 将四个 \n 替换为两个 \n
        file_content = file_content.replace('\n\n\n\n', '\n\n')
        file_content = file_content.replace('\n\n \n\n', '\n\n').replace('\n\n \n\n', '\n\n')
        return file_content


