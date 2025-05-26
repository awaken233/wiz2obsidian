import re
import unittest


class TestRegexOnly(unittest.TestCase):
    """独立的正则表达式测试，不依赖API"""

    def _extract_attachment_links_from_markdown(self, content):
        """
        从markdown内容中提取附件链接，排除图片链接
        :param content: markdown内容
        :return: 附件文件名列表
        """
        # 使用负向前瞻排除图片链接 ![text](url)，只匹配普通链接 [text](url)
        pattern = r'(?<!!)\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        # 返回链接URL部分（文件名）
        return [match[1] for match in matches]

    def test_extract_attachment_links_from_markdown(self):
        """测试从markdown内容中提取附件链接的正则表达式功能"""
        print("开始测试正则表达式提取附件链接功能")
        
        # 测试数据：包含各种类型的链接
        test_content = """
# 测试文档

这是一个包含多种链接的测试文档。

## 图片链接（应该被排除）
![测试图片1](image1.png)
![测试图片2](./images/image2.jpg)
![远程图片](https://example.com/image.png)

## 附件链接（应该被提取）
[文档附件1](document1.pdf)
[表格文件](spreadsheet.xlsx)
[压缩包](archive.zip)
[本地文件](./files/data.txt)

## 普通链接（应该被提取）
[外部链接](https://example.com)
[相对链接](../other/page.html)

## 混合内容
这里有一个图片 ![内联图片](inline.png) 和一个附件 [重要文档](important.docx)。
        """
        
        # 调用被测试的方法
        attachment_links = self._extract_attachment_links_from_markdown(test_content)
        
        # 验证结果
        expected_links = [
            'document1.pdf',
            'spreadsheet.xlsx', 
            'archive.zip',
            './files/data.txt',
            'https://example.com',
            '../other/page.html',
            'important.docx'
        ]
        
        print(f"提取到的附件链接: {attachment_links}")
        print(f"预期的附件链接: {expected_links}")
        
        # 验证提取的链接数量和内容
        self.assertEqual(len(attachment_links), len(expected_links))
        for expected_link in expected_links:
            self.assertIn(expected_link, attachment_links)
        
        # 确保图片链接没有被错误提取
        image_links = ['image1.png', './images/image2.jpg', 'https://example.com/image.png', 'inline.png']
        for image_link in image_links:
            self.assertNotIn(image_link, attachment_links)
        
        print("正则表达式提取附件链接功能测试完成")


if __name__ == '__main__':
    unittest.main() 