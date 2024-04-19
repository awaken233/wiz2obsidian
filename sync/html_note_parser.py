from sync.note_parser import NoteParser
from sync.note_fixer import NoteFixer
import html2text


class HtmlNoteParser(NoteParser):
    def parse_content(self, origin_content):
        markdown_content = html2text.html2text(origin_content)
        # 一些后置处理
        file_content = NoteFixer.fix(markdown_content)
        return file_content


