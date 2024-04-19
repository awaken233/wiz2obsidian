from abc import ABC, abstractmethod
import re
from sync.parsed_note import ParsedNote
from log import log


class NoteParser(ABC):
    @abstractmethod
    def parse_content(self, origin_content):
        pass

    def process_content(self, origin_content):
        parsed_content = self.parse_content(origin_content)
        extract_images = self._extract_images(parsed_content)
        return ParsedNote(parsed_content, extract_images)

    # 提取图片
    @staticmethod
    def _extract_images(parsed_content):
        regex = r"!\[.*?\]\((.*?)\)"
        img_names = re.findall(regex, parsed_content)
        # 过滤掉 http https 开头的图片
        img_names = list(filter(lambda x: not x.startswith('http'), img_names))
        # 如果是 index_files/ 开头的 trim 掉
        img_names = list(map(lambda x: x.replace('index_files/', ''), img_names))
        # 过滤掉 data:image/png;base64 开头的
        img_names = list(filter(lambda x: not x.startswith('data:image'), img_names))
        # 过滤掉空字符串
        img_names = list(filter(lambda x: x != '', img_names))
        # 去重
        img_names = list(set(img_names))
        return img_names
