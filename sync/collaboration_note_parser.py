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
        text_content = '\n' + self.handle_text_obj_text(block_row) + '\n'
        # 检查是否有评论，如果有则添加评论内容
        comment_content = self.handle_comments(block_row)
        return text_content + comment_content

    def handle_text_obj_text(self, block_row):
        # 注意：此方法忽略align属性（居中、左对齐、右对齐），只处理文本内容
        if block_row.get("quoted"):
            return self.handle_quote(block_row['text'])
        elif block_row.get("heading"):
            return self.handle_header(block_row, block_row['text'])
        else:
            return self.handle_text(block_row['text'])

    def handle_comments(self, block_row):
        """处理评论内容"""
        comments_content = []
        
        # 检查文本中是否有评论引用
        for text_dict in block_row.get('text', []):
            attributes = text_dict.get('attributes', {})
            for attr_key, comment_id in attributes.items():
                if attr_key.startswith('comment-'):
                    # 从全局comments数据中获取评论信息
                    comment_data = self.data.get('comments', {}).get(comment_id)
                    if comment_data:
                        comment_text = self.format_comment(comment_data)
                        comments_content.append(comment_text)
                        
                        # 检查是否有子评论
                        group_id = comment_data.get('groupId')
                        if group_id:
                            sub_comments = self.get_sub_comments(group_id, comment_id)
                            comments_content.extend(sub_comments)
        
        return ''.join(comments_content)

    def format_comment(self, comment_data):
        """格式化单个评论"""
        display_name = comment_data.get('displayName', '未知用户')
        created_timestamp = comment_data.get('created', 0)
        
        # 转换时间戳为可读格式
        import datetime
        try:
            dt = datetime.datetime.fromtimestamp(created_timestamp / 1000)  # 毫秒转秒
            # 判断上午还是下午
            if dt.hour < 12:
                time_period = '上午'
                hour = dt.hour if dt.hour != 0 else 12
            else:
                time_period = '下午'
                hour = dt.hour if dt.hour <= 12 else dt.hour - 12
            
            formatted_time = f"{dt.year}/{dt.month}/{dt.day} {time_period}{hour}:{dt.minute:02d}:{dt.second:02d}"
        except:
            formatted_time = '时间未知'
        
        # 处理评论内容块
        comment_text_parts = []
        for block in comment_data.get('blocks', []):
            for text_dict in block.get('text', []):
                if text_dict.get('attributes', {}).get('type') == 'mention':
                    # 处理@提及
                    mention_text = text_dict.get('attributes', {}).get('text', '')
                    comment_text_parts.append(f'@{mention_text}')
                else:
                    comment_text_parts.append(text_dict.get('insert', ''))
        
        comment_text = ''.join(comment_text_parts)
        
        return f'\n\n> {display_name} {formatted_time}\n\n{comment_text}\n'

    def get_sub_comments(self, group_id, main_comment_id):
        """获取同一组中的其他评论（子评论）"""
        sub_comments = []
        all_comments = self.data.get('comments', {})
        
        for comment_id, comment_data in all_comments.items():
            if (comment_data.get('groupId') == group_id and 
                comment_id != main_comment_id):
                sub_comment_text = self.format_comment(comment_data)
                sub_comments.append(sub_comment_text)
        
        return sub_comments
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
        return ''.join(text) + "\n"

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
        elif embed_type == "toc":
            return "\n\n[TOC]\n\n"
        elif embed_type == "hr":
            return "\n\n---\n\n"
        elif embed_type == "office":
            # 附件 []() - 使用特殊标记确保正则提取的准确性
            file_name = row['embedData'].get('fileName', '')
            src = row['embedData'].get('src', '')
            return f'\n\n[{file_name}](wiz-collab-attachment://{src})\n\n'
        elif embed_type == "snapshot":
            return self.handle_snapshot(embed_data)
        elif embed_type == "encrypt-text":
            # 忽略加密文本，不解析内容
            return ""
        elif embed_type == "webpage":
            return self.handle_webpage(embed_data)
        elif embed_type == "drawio":
            return self.handle_drawio(embed_data)
        elif embed_type == "mermaid":
            return self.handle_mermaid(embed_data)
        else:
            log.error(f"Unsupported embed type: {embed_type}")
            return ""  # 返回空字符串而不是 None

    def handle_image(self, embed_data):
        image_url = embed_data["src"]
        file_name = embed_data.get('fileName', '')
        return f"![{file_name}]({image_url})\n\n"

    def handle_snapshot(self, embed_data):
        """处理快照嵌入类型 - 递归解析完整内容并格式化为引用块"""
        try:
            # 解析嵌套的doc内容
            doc_content = embed_data.get("doc", "")
            if doc_content:
                doc_json = json.loads(doc_content)
                
                # 递归解析嵌套doc的blocks
                nested_blocks = doc_json.get("blocks", [])
                nested_content = []
                
                for block in nested_blocks:
                    # 使用现有的MarkdownConverter解析每个block
                    block_content = MarkdownConverter.to_text(doc_json, block)
                    nested_content.append(block_content)
                
                # 将解析的内容组合并转换为引用块格式
                combined_content = ''.join(nested_content).strip()
                
                # 按行分割并为每行添加引用前缀
                lines = combined_content.split('\n')
                quoted_lines = []
                
                for line in lines:
                    # 为每一行添加 "> " 前缀，包括空行
                    quoted_lines.append(f"> {line}")
                
                result = "\n\n" + '\n'.join(quoted_lines) + "\n\n"
                return result
            else:
                return "\n\n> **嵌入快照**: 无内容\n\n"
        except (json.JSONDecodeError, KeyError) as e:
            log.error(f"解析snapshot嵌入内容失败: {e}")
            return "\n\n> **嵌入快照**: 解析失败\n\n"

    def handle_webpage(self, embed_data):
        """处理网页嵌入类型"""
        src = embed_data.get("src", "")
        return f"\n\n[webpage]({src})\n\n"

    def handle_drawio(self, embed_data):
        """处理流程图类型 - 使用和附件相同的处理逻辑"""
        src = embed_data.get("src", "")
        # 流程图没有fileName字段，使用固定名称
        file_name = "流程图"
        return f'\n\n[{file_name}](wiz-collab-attachment://{src})\n\n'

    def handle_mermaid(self, embed_data):
        """处理 mermaid 流程图类型"""
        mermaid_text = embed_data.get("mermaidText", "")
        if mermaid_text:
            # 将 mermaid 文本转换为 markdown 代码块格式
            return f'\n\n```mermaid\n{mermaid_text}\n```\n\n'
        else:
            # 如果没有 mermaidText，尝试使用 src 作为附件链接
            src = embed_data.get("src", "")
            if src:
                file_name = "Mermaid流程图"
                return f'\n\n[{file_name}](wiz-collab-attachment://{src})\n\n'
            else:
                return '\n\n```mermaid\n# Mermaid 图表内容缺失\n```\n\n'


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
            if attributes.get("type") == "wiki-link":
                return BlockTextConverter.handle_wiki_link(text_dict)
            elif attributes.get("type") == "math":
                return BlockTextConverter.handle_math(text_dict)
            elif attributes.get("link"):
                return BlockTextConverter.handle_link(text_dict)
            elif attributes.get("style-code"):
                return BlockTextConverter.handle_code(text_dict)
            elif attributes.get("style-italic"):
                return BlockTextConverter.handle_italic(text_dict)
            elif attributes.get("style-bold"):
                return BlockTextConverter.handle_bold(text_dict)
            elif attributes.get('style-strikethrough'):
                return BlockTextConverter.handle_strikethrough(text_dict)
            elif attributes.get('style-super'):
                # 忽略上标格式，直接返回文本
                return BlockTextConverter.handle_text(text_dict)
            elif attributes.get('style-sub'):
                # 忽略下标格式，直接返回文本
                return BlockTextConverter.handle_text(text_dict)
            # 处理文字颜色和背景颜色.
            elif any(key.startswith("style-color-") or key.startswith("style-bg-color-") for key in attributes.keys()):
                return BlockTextConverter.handle_highlight(text_dict)
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

    @classmethod
    def handle_highlight(cls, text_dict):
        return f'=={text_dict["insert"]}=='

    @classmethod
    def handle_wiki_link(cls, text_dict):
        """处理wiki链接类型"""
        attributes = text_dict["attributes"]
        name = attributes.get("name", "")
        secondary_name = attributes.get("secondaryName", "")
        
        # 移除name中的.md后缀
        if name.endswith('.md'):
            name = name[:-3]
        
        # 如果有secondaryName，使用Obsidian风格的语法 [[显示名称|链接]]
        if secondary_name:
            return f'[[{secondary_name}|{name}]]'
        else:
            return f'[[{name}]]'

    @classmethod
    def handle_math(cls, text_dict):
        """处理数学公式类型"""
        attributes = text_dict["attributes"]
        tex = attributes.get("tex", "")
        # 去除tex内容前后的空格，并转换为行内数学公式格式
        tex_content = tex.strip()
        return f'${tex_content}$'


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
        strategy: BaseStrategy = MarkdownConverter.create_strategy(data, block_row)
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