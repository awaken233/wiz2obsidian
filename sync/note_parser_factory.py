from log import log
from .collaboration_note_parser import CollaborationNoteParser
from .html_note_parser import HtmlNoteParser
from .note import Note
from .lite_note_parser import LiteNoteParser
import re


class NoteParserFactory:

    @staticmethod
    def create_parser(note_type, title=None):
        """
        根据笔记类型创建笔记解析器, 如下是我的笔记类型.
        +-------------+--------+
        |type         |count(*)|
        +-------------+--------+
        |             |127     |
        |collaboration|192     |
        |document     |644     |
        |lite/markdown|256     |
        |markdown     |1       |
        |svgpainter   |1       |
        |tasklist     |5       |
        +-------------+--------+
        :param note_type: 笔记类型
        :param title: 笔记标题
        :return: 笔记解析器
        """
        if Note.is_collaboration_note(note_type):
            return CollaborationNoteParser()
        elif note_type == 'lite/markdown':
            return LiteNoteParser()
        else:
            return HtmlNoteParser()