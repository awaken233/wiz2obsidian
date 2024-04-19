import json
from log import log
from sync.note_parser import NoteParser
from sync.note_fixer import NoteFixer



class BaseStrategy:

    def __init__(self, data):
        self.data = data

    def to_text(self, block_row):
        pass


class TextStrategy(BaseStrategy):
    def to_text(self, block_row):
        return '\n' + self.handle_text_obj_text(block_row) + '\n'

    def handle_text_obj_text(self, block_row):
        if block_row.get("quoted"):
            return self.handle_quote(block_row['text'])
        elif block_row.get("heading"):
            return self.handle_header(block_row, block_row['text'])
        else:
            return self.handle_text(block_row['text'])
    @staticmethod
    def handle_text(text_arr):
        # 判断是否是空数组
        if not text_arr:
            return ''

        text = []
        for text_dict in text_arr:
            text.append(BlockTextConverter.to_text(text_dict))
        return ''.join(text)

    @staticmethod
    def handle_header(block_row, text_arr):
        text = []
        heading_level = block_row.get("heading")
        text.append(f'{"#" * heading_level} ')
        for text_dict in text_arr:
            text.append(BlockTextConverter.to_text(text_dict))
        return ''.join(text)

    @staticmethod
    def handle_quote(json_data):
        text = []
        text.append("> ")
        for text_dict in json_data:
            text.append(BlockTextConverter.to_text(text_dict))
        join = ''.join(text)
        return join + '\n'


class ListStrategy(BaseStrategy):
    def to_text(self, block_row):
        # block_row.ordered 判断true false 来确定是有序列表还是无序
        if block_row.get("ordered"):
            return self.handle_ordered_list(block_row)
        else:
            return self.handle_unordered_list(block_row)

    def handle_unordered_list(self, block_row):
        text = []
        indent = (block_row['level'] - 1) * 2 * ' '
        text.append(f'{indent}- ')
        # 判断 block_row 是否含有 checkbox 属性, 如果该属性等于 checked, 需要添加 [], 如果该属性等于unchecked, 需要添加[x]
        if block_row.get("checkbox"):
            if block_row["checkbox"] == "checked":
                text.append("[x] ")
            elif block_row["checkbox"] == "unchecked":
                text.append("[ ] ")
            else:
                raise ValueError(f"Unsupported checkbox value: {block_row['checkbox']}")

        for text_dict in block_row["text"]:
            text.append(BlockTextConverter.to_text(text_dict))
        join = ''.join(text)
        return join+'\n'

    def handle_ordered_list(self, block_row):
        text = []
        indent = (block_row['level'] - 1) * 2 * ' '
        text.append(f'{indent}{block_row["start"]}. ')
        for text_dict in block_row["text"]:
            text.append(BlockTextConverter.to_text(text_dict) + '\n')
        return ''.join(text)


class CodeStrategy(BaseStrategy):

    def __init__(self, data):
        super().__init__(data)

    def to_text(self, row):
        # 解析 language
        language = row["language"]
        # 获取children中的第一个元素作为id,从全局data中获取
        code_id = row["children"][0]
        texts = []
        for text_obj in self.data[code_id]:
            # 如果 text_ 是空的话, 插入空行, 否则插入insert节点
            text_ = text_obj['text'][0] if text_obj['text'] else {"insert": ""}
            texts.append(text_["insert"] + "\n")
        return f"```{language}\n{''.join(texts)}```\n\n"


class EmbedStrategy(BaseStrategy):

    def __init__(self, data):
        super().__init__(data)

    def to_text(self, row):
        embed_type = row["embedType"]
        embed_data = row["embedData"]
        if embed_type == "image":
            return self.handle_image(embed_data)
        # toc 和 hr
        if embed_type == "toc":
            return "\n\n[TOC]\n\n"
        elif embed_type == "hr":
            return "\n\n---\n\n"
        elif embed_type == "office":
            # 附件 []()
            file_name = row['embedData'].get('fileName', '')
            src = row['embedData'].get('src', '')
            return f'\n\n[{file_name}]({src})\n\n'
        else:
            log.error(f"Unsupported embed type: {embed_type}")

    def handle_image(self, embed_data):
        image_url = embed_data["src"]
        file_name = embed_data.get('fileName', '')
        return f"![{file_name}]({image_url})\n\n"


class TableStrategy(BaseStrategy):

    def __init__(self, data):
        super().__init__(data)

    def to_text(self, row):
        cols = row["cols"]
        rows = row["rows"]
        children = row["children"]

        # 下面的代码需要考虑 self.data[child_id][0]["text"] 是 空的情况
        children_text = []
        for child_id in children:
            text_ = self.data[child_id][0]["text"][0]['insert'] if self.data[child_id][0]["text"] else ''
            children_text.append(text_)
        headers = children_text[:cols]
        body = children_text[cols:]

        markdown_table = "|".join(headers)
        markdown_table = "|" + markdown_table + "|\n"
        markdown_table += "| " + " | ".join(["-----"] * cols) + " |\n"

        # 对 body 按照 cols slice
        body_rows = [body[i:i + cols] for i in range(0, len(body), cols)]

        for body_row in body_rows:
            markdown_table += "|" + "|".join(body_row) + "|\n"
        return '\n' + markdown_table + '\n'


class BlockTextConverter:

    @staticmethod
    def to_text(text_dict):
        # 判断 text 中存在属性 attributes, 存在需要判断是不是 link, style-code, style-italic,style-bold, style-strikethrough
        # 如果都不存在当作普通文本
        if text_dict.get("attributes"):
            attributes = text_dict["attributes"]
            if attributes.get("link"):
                return BlockTextConverter.handle_link(text_dict)
            elif attributes.get("style-code"):
                return BlockTextConverter.handle_code(text_dict)
            elif attributes.get("style-italic"):
                return BlockTextConverter.handle_italic(text_dict)
            elif attributes.get("style-bold"):
                return BlockTextConverter.handle_bold(text_dict)
            elif attributes.get('style-strikethrough'):
                return BlockTextConverter.handle_strikethrough(text_dict)
            else:
                return BlockTextConverter.handle_text(text_dict)
        else:
            return BlockTextConverter.handle_text(text_dict)

    @classmethod
    def handle_link(cls, text_dict):
        return f'[{text_dict["insert"]}]({text_dict["attributes"]["link"]})'

    @classmethod
    def handle_code(cls, text_dict):
        return f'`{text_dict["insert"]}`'

    @classmethod
    def handle_italic(cls, text_dict):
        return f'*{text_dict["insert"]}*'

    @classmethod
    def handle_text(cls, text_dict):
        return text_dict["insert"]

    @classmethod
    def handle_bold(cls, text_dict):
        return f'**{text_dict["insert"]}**'

    @classmethod
    def handle_strikethrough(cls, text_dict):
        return f'~~{text_dict["insert"]}~~'


class MarkdownConverter:
    STRATEGY_MAP = {
        "text": TextStrategy,
        "list": ListStrategy,
        "code": CodeStrategy,
        "table": TableStrategy,
        "embed": EmbedStrategy
    }

    def __init__(self):
        pass

    @staticmethod
    def to_text(data, block_row):
        strategy = MarkdownConverter.create_strategy(data, block_row)
        return strategy.to_text(block_row)

    @staticmethod
    def create_strategy(data, json_data):
        strategy_type = json_data["type"]
        strategy_class = MarkdownConverter.STRATEGY_MAP.get(strategy_type)
        if strategy_class:
            return strategy_class(data)
        else:
            log.error(f"Unsupported type: {strategy_type}")


class CollaborationNoteParser(NoteParser):
    def parse_content(self, origin_content):
        markdown_content = self.parse(origin_content)
        file_content = NoteFixer.fix(markdown_content)
        return file_content

    def parse(self, origin_content):
        log.info(f'协作笔记解析笔记 原始内容: \n {origin_content}')
        json_content = json.loads(origin_content)
        text = []
        for block_row in json_content['data']['data']["blocks"]:
            text.append(MarkdownConverter.to_text(json_content['data']['data'], block_row))
        content = ''.join(text)
        return content