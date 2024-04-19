
class Note:

    # 是否是协作笔记静态方法
    @staticmethod
    def is_collaboration_note(note_type):
        if note_type in ['collaboration']:
            return True
        return False
