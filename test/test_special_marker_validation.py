import unittest
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync.note_synchronizer import NoteSynchronizer
from sync.wiz_open_api import WizOpenApi
from sync.database import Database
from sync.config import config
from log import log


class TestSpecialMarkerValidation(unittest.TestCase):
    """特殊标记机制验证测试类"""

    def setUp(self):
        """测试前的设置"""
        # 创建NoteSynchronizer实例（用于测试正则表达式方法）
        # 为了测试正则表达式，我们不需要真实的API连接
        self.synchronizer = NoteSynchronizer(None, None)

    def test_comprehensive_link_extraction_accuracy(self):
        """综合测试：验证特殊标记机制的链接提取准确性"""
        log.info("开始综合验证特殊标记机制的准确性")

        # 构造包含各种复杂情况的测试内容
        complex_test_content = """
# 复杂链接测试文档

## 1. 图片链接（应该被完全忽略）
![普通图片](image.png)
![远程图片](https://cdn.example.com/photo.jpg)
![本地图片](./images/local.gif)

## 2. 协作笔记附件（应该被准确提取）
[文档附件](wiz-collab-attachment://document.pdf)
[表格文件](wiz-collab-attachment://data.xlsx)
[压缩包](wiz-collab-attachment://archive.zip)

## 3. 普通链接（应该被完全忽略）
[外部网站](https://www.example.com)
[GitHub项目](https://github.com/user/repo)
[本地页面](./page.html)
[相对路径](../other/file.md)
[邮箱链接](mailto:user@example.com)
[FTP链接](ftp://ftp.example.com/file.txt)

## 4. 混合复杂场景
这是一段包含多种链接的文字：
- 有一个图片 ![内联图片](inline.png)
- 有一个协作笔记附件 [重要文档](wiz-collab-attachment://important.docx)
- 有一个普通链接 [官方网站](https://official.site)
- 还有另一个附件 [配置文件](wiz-collab-attachment://config.json)

## 5. 边界情况测试
[看起来像附件但不是](file://local/path.txt)
[另一个类似链接](wiz-attachment://fake.pdf)
[正确的附件](wiz-collab-attachment://real-file.docx)

## 6. 特殊字符和编码
[中文附件](wiz-collab-attachment://中文文档.pdf)
[带空格附件](wiz-collab-attachment://file with spaces.txt)
[特殊字符附件](wiz-collab-attachment://file-name_123.xlsx)

## 7. 嵌套和转义情况
\[转义链接\](wiz-collab-attachment://escaped.pdf)
[[双重括号]](wiz-collab-attachment://double-bracket.txt)

> 引用块中的附件：[引用附件](wiz-collab-attachment://quoted-file.zip)
> 引用块中的普通链接：[引用链接](https://quoted.link.com)

| 表格 | 附件列 | 链接列 |
|------|--------|---------|
| 行1 | [表格附件](wiz-collab-attachment://table-file.csv) | [表格链接](https://table.link) |

```代码块
[代码中的附件](wiz-collab-attachment://code-file.py)
[代码中的链接](https://code.link)
```
        """

        # 执行提取
        extracted_links = self.synchronizer._extract_attachment_links_from_markdown(complex_test_content)

        # 预期的附件列表（只有使用特殊标记的才应该被提取）
        expected_attachments = [
            'document.pdf',
            'data.xlsx',
            'archive.zip',
            'important.docx',
            'config.json',
            'real-file.docx',
            '中文文档.pdf',
            'file with spaces.txt',
            'file-name_123.xlsx',
            'double-bracket.txt',  # 双重括号应该被提取
            'quoted-file.zip',
            'table-file.csv'
            # 注意：转义链接和代码块中的链接不应该被提取
        ]

        # 不应该被提取的链接（验证没有误匹配）
        excluded_items = [
            'image.png', 'https://cdn.example.com/photo.jpg', './images/local.gif',  # 图片
            'https://www.example.com', 'https://github.com/user/repo', './page.html',  # 普通链接
            '../other/file.md', 'mailto:user@example.com', 'ftp://ftp.example.com/file.txt',
            'inline.png', 'https://official.site',  # 混合场景中的非附件
            'file://local/path.txt', 'wiz-attachment://fake.pdf',  # 错误格式
            'https://quoted.link.com', 'https://table.link',  # 表格和引用中的普通链接
            'code-file.py', 'https://code.link'  # 代码块中的链接（这些实际上不会被处理）
        ]

        log.info(f"提取到的附件: {extracted_links}")
        log.info(f"预期的附件: {expected_attachments}")

        # 验证提取的附件数量和内容完全正确
        self.assertEqual(len(extracted_links), len(expected_attachments), 
                        f"提取的附件数量不正确。预期: {len(expected_attachments)}, 实际: {len(extracted_links)}")

        for expected_attachment in expected_attachments:
            self.assertIn(expected_attachment, extracted_links, 
                         f"预期的附件 '{expected_attachment}' 没有被提取到")

        # 验证没有误提取任何非附件链接
        for excluded_item in excluded_items:
            self.assertNotIn(excluded_item, extracted_links, 
                           f"非附件项目 '{excluded_item}' 被错误提取了")

        log.info("特殊标记机制验证通过：准确提取了所有协作笔记附件，没有误匹配任何普通链接")

    def test_edge_case_regex_patterns(self):
        """测试边界情况和特殊正则模式"""
        log.info("开始测试边界情况和特殊正则模式")

        edge_cases = [
            # 测试用例：(内容, 预期提取的附件数量, 描述)
            ("", 0, "空字符串"),
            ("[text](wiz-collab-attachment://file.pdf)", 1, "单个正确附件"),
            ("[text](wiz-collab-attachment://)", 0, "空文件名附件（应该被过滤）"),
            ("[](wiz-collab-attachment://file.pdf)", 1, "空链接文本"),
            ("[text](WIZ-COLLAB-ATTACHMENT://file.pdf)", 0, "大写协议（应该不匹配）"),
            ("[text](wiz-collab-attachment://file.pdf) [text2](https://example.com)", 1, "混合链接"),
            ("[text](wiz-collab-attachment://file1.pdf) [text2](wiz-collab-attachment://file2.txt)", 2, "多个附件"),
            ("![image](wiz-collab-attachment://file.pdf)", 0, "图片语法（应该不匹配）"),
            ("\\[escaped\\](wiz-collab-attachment://file.pdf)", 0, "转义链接"),
            ("[text](wiz-collab-attachment://very/long/path/to/file.extension)", 1, "长路径"),
        ]

        for test_content, expected_count, description in edge_cases:
            with self.subTest(description=description):
                extracted = self.synchronizer._extract_attachment_links_from_markdown(test_content)
                self.assertEqual(len(extracted), expected_count, 
                               f"{description}: 预期 {expected_count} 个附件，实际 {len(extracted)} 个")

        log.info("边界情况测试完成")

    def test_performance_with_large_content(self):
        """测试大内容的性能表现"""
        log.info("开始测试大内容性能")

        # 生成大量内容进行性能测试
        large_content_parts = []
        for i in range(1000):
            large_content_parts.append(f"[普通链接{i}](https://example{i}.com)")
            if i % 10 == 0:  # 每10个普通链接中插入1个附件链接
                large_content_parts.append(f"[附件{i}](wiz-collab-attachment://file{i}.pdf)")

        large_content = "\n".join(large_content_parts)

        import time
        start_time = time.time()
        extracted = self.synchronizer._extract_attachment_links_from_markdown(large_content)
        end_time = time.time()

        processing_time = end_time - start_time
        log.info(f"处理包含 {len(large_content_parts)} 行内容耗时: {processing_time:.4f} 秒")
        log.info(f"提取到 {len(extracted)} 个附件")

        # 验证只提取了附件，没有普通链接
        expected_attachment_count = len([p for p in large_content_parts if 'wiz-collab-attachment://' in p])
        self.assertEqual(len(extracted), expected_attachment_count)

        # 性能断言：处理时间应该在合理范围内（比如1秒以内）
        self.assertLess(processing_time, 1.0, "大内容处理性能不符合预期")

        log.info("大内容性能测试通过")


if __name__ == '__main__':
    unittest.main() 