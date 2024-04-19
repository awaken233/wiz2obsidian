from sync.note_parser import NoteParser
from bs4 import BeautifulSoup
from sync.note_fixer import NoteFixer


class LiteNoteParser(NoteParser):
    def parse_content(self, origin_content):
        markdown_content = self.parse(origin_content)
        file_content = NoteFixer.fix(markdown_content)
        return file_content

    @staticmethod
    def parse(origin_content):
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(origin_content, 'html.parser')
        # 首先找到body标签
        body_tag = soup.find('body')
        # 然后在body标签下找到第一个pre标签
        first_pre_tag = body_tag.find('pre')  # 默认就会找到第一个匹配的pre标签
        # 获取pre标签中的文本内容
        text_content = first_pre_tag.get_text()
        return text_content
