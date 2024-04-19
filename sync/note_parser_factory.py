from log import log
from .collaboration_note_parser import CollaborationNoteParser
from .html_note_parser import HtmlNoteParser
from .note import Note
from .lite_note_parser import LiteNoteParser
import re


class NoteParserFactory:
    @staticmethod
    def create_parser(note_type):
        if Note.is_collaboration_note(note_type):
            return CollaborationNoteParser()
        elif note_type == 'lite/markdown':
            return LiteNoteParser()
        else:
            return HtmlNoteParser()