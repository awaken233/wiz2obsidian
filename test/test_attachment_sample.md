# 附件处理测试文档

这是一个专门用于测试附件处理功能的markdown文档。

## 图片链接（应该被正则表达式排除）

![图片1](test-image1.png)
![图片2](./images/test-image2.jpg)
![远程图片](https://cdn.example.com/remote-image.png)

## 协作笔记附件链接（应该被正则表达式提取，使用特殊标记）

[PDF文档](wiz-collab-attachment://test-document.pdf)
[Excel表格](wiz-collab-attachment://data-sheet.xlsx)
[Word文档](wiz-collab-attachment://report.docx)
[压缩包](wiz-collab-attachment://archive.zip)
[文本文件](wiz-collab-attachment://readme.txt)

## 普通附件链接（应该被排除，没有特殊标记）

[配置文件](./config/app.conf)
[本地文档](local-file.pdf)

## 普通链接（应该被排除）

[外部网站](https://www.example.com)
[相对链接](../other/page.html)
[本地页面](./local/index.html)

## 混合内容测试

这段文字包含一个图片 ![内联图片](inline-pic.jpg) 和一个协作笔记附件 [重要文件](wiz-collab-attachment://important-file.docx)，还有一个普通链接 [官网](https://official.site)。

## 特殊格式测试

- 列表中的图片：![列表图片](list-image.png)
- 列表中的附件：[列表附件](wiz-collab-attachment://list-file.pdf)

> 引用块中的图片：![引用图片](quote-image.png)
> 引用块中的附件：[引用附件](wiz-collab-attachment://quote-file.txt)

### 表格中的链接

| 类型 | 图片 | 附件 |
|------|------|------|
| 示例 | ![表格图片](table-image.png) | [表格附件](wiz-collab-attachment://table-file.csv) |

## 代码块（应该被忽略）

```markdown
![代码块图片](code-image.png)
[代码块附件](code-file.json)
```

## 转义字符测试

\![转义图片](escaped-image.png)
\[转义附件](escaped-file.txt) 