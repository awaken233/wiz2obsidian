## 功能

使用python将为知笔记中的所有笔记都导出到本地, 转化为纯markdown文本文件.

## 前置准备

- 启动picgo(version >= 2.1.0), 并配置picgo图床,测试上传成功
- 将所有加密笔记取消加密
- `conf/config.yaml` 配置位置笔记的用户名和密码

导包, 运行 main.py 即可.
## 注意

- 笔记标题和目录名不要出现 `/`等和文件分隔符冲突的特殊字符, 无法导出
- 我 picgo 配置的是github图片,不允许出现同名文件名, 会导致上传错误, 导致部分图片上传错误
- 为知笔记应用不要打开协作笔记tab页, 否则影响程序读取读取该笔记的数据.


## 项目结构

```
├── conf
│   ├── conf.yaml  // 配置文件, 需要配置帐号密码
│   └── logging.yaml // 日志配置
├── log.py
├── main.py // 主程序入口
├── output
│   ├── db
│   │   └── sync.db // sqlite3 记录笔记同步记录和笔记图片同步记录
│   ├── export_image // 笔记图片, 目录结构为: 笔记的文件夹目录/笔记名/笔记下所有图片
│   ├── note         // 所有导出 markdown 笔记
│   └── log
│       └── log.log // 日志
├── sync // 同步程序
└── test // 测试相关
```


## 相关问题

### 协作笔记如何处理

协作笔记使用ws通信, 返回特定的数据格式, 需要写解析器将其解析为markdown纯文本.
[GitHub - websocket-client/websocket-client: WebSocket client for Python](https://github.com/websocket-client/websocket-client)

因为使用ws通信, 为知笔记应用不要打开协作笔记, 否则影响程序读取读取该笔记的数据.

### 如何处理笔记附件

忽略笔记中的附件, 不处理.

### 如何处理加密笔记

将所有加密笔记取消加密, 当作常规笔记处理, 避免处理加密笔记的复杂性.
[WizNote 加密笔记](https://www.wiz.cn/ziw-format.html)

### 如何处理笔记中的图片

程序将笔记中的图片下载到本地, 通过picgo http api上传图片并替换图片地址.(请启动picgo, 并配置picgo图床,测试上传成功)
[高级技巧 | PicGo](https://picgo.github.io/PicGo-Doc/zh/guide/advance.html#picgo-server%E7%9A%84%E4%BD%BF%E7%94%A8)

### 如何处理笔记的tag

忽略原先为知笔记中的tag, 将笔记的目录作为tag.


## 不同笔记类型处理方式

随着为知笔记的发展, 有如下类型的笔记
- HTML 笔记. 最初的, 使用富文本编辑器编辑的笔记
- Lite 笔记. 依旧使用富文本编辑器, 标题名需要以`.md` 结尾, 需要在富文本编辑器中写 markdown 文本, 进入预览模式才会进行md渲染.
- 协作笔记. 现在最新的笔记格式, 支持多人协作.

项目支持处理以下几种类型的笔记：

- HTML 笔记（document）
   - 使用 `html2text` 库直接将 HTML 转换为 Markdown. 解析后的markdown文本, 差强人意, 完全取决于富文本的格式.

- Lite 笔记（lite/markdown）
   - 通过 BeautifulSoup 库解析 HTML 内容
   - 提取 pre 标签中的原始 Markdown 文本

- 协作笔记（collaboration）
   - 通过自定义解析器处理, 手动解析拼装.
   - 支持解析文本、列表、代码块、表格、图片等多种格式
   - 使用 WebSocket 通信获取笔记数据

所有类型的笔记在解析后都会经过以下处理：
- 提取并下载笔记中的图片
- 通过 PicGo 上传图片到图床
- 替换笔记中的图片链接
- 添加笔记属性（创建时间、更新时间、标签等）
- 进行 Markdown 格式优化（标题、代码块、列表等的格式修正）


## 其他

半吊子python, 程序还有很多不完善之处. 待其他人完善.

程序的默认导出约定更多是符合我自己的期望, 而不是做成一个通用的工具产品. 待其他人有时间完善吧, 比如:
- 忽略原先为知笔记中的tag, 将笔记的目录作为tag, 因为我自己不用为知的tag.
- 忽略加密笔记的处理(因为我没有几篇加密笔记,直接取消加密即可, 不用为了处理加密笔记的解析写多余的代码)
- ...等等


待完善之处

- 程序可以打包成app, exe, 让不懂程序的人也能轻松使用
- 配置导出参数, 可以更好的定制化导出
- 上传到图床, 图片名不能相同. (目标图片名可以用时间戳, 同步笔记图片表记录目标文件名,  导出的时候替换目标文件名)
- 公式, 流程图解析可能存在问题.


## 参考文章

[[WizNote 为知笔记 macOS 本地文件夹分析 | ZRONG's BLOG](https://blog.zengrong.net/post/analysis-of-wiznote/)

[server-architecture.md](https://github.com/WizTeam/wiz-editor/blob/main/docs/zh-CN/server-architecture.md)

[GitHub - WizTeam/wiz-editor](https://github.com/WizTeam/wiz-editor)

[为知笔记API文档](https://www.wiz.cn/wapp/pages/book/bb8f0f10-48ca-11ea-b27a-ef51fb9d4bb4/475c9ef0-4e1a-11ea-8f5c-a7618da01da2)