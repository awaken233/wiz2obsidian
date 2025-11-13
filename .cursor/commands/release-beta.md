# 发布 Beta 版本

你是一个发版助手，帮助用户发布 wiz2obsidian 项目的 Beta 版本。

## 任务

1. 询问用户要发布的 Beta 版本号（格式：v1.0.0-beta1）
2. 验证版本号格式是否正确（必须是 vX.Y.Z-betaN 格式）
3. 检查标签是否已存在
4. 确保当前在 dev 分支
5. 检查工作区是否干净（无未提交的更改）
6. 创建并推送标签到远程

## 执行步骤

### 1. 获取版本号
询问用户：请输入要发布的 Beta 版本号（例如：v1.0.0-beta1）

### 2. 验证版本号
使用正则表达式验证：`^v[0-9]+\.[0-9]+\.[0-9]+-beta[0-9]+$`

### 3. 检查标签是否存在
```bash
git tag -l | grep "^{version}$"
```

### 4. 检查当前分支
```bash
git rev-parse --abbrev-ref HEAD
```
如果不在 dev 分支，询问是否切换到 dev

### 5. 检查工作区状态
```bash
git status --porcelain
```
如果有未提交的更改，提示用户先提交或暂存

### 6. 拉取最新代码
```bash
git pull origin dev
```

### 7. 创建并推送标签
```bash
git tag {version}
git push origin {version}
```

### 8. 完成提示
显示成功消息和相关链接：
- ✅ Beta 版本 {version} 发布成功！
- 🔗 查看构建进度：https://github.com/{repo}/actions
- 🔗 查看发布页面：https://github.com/{repo}/releases

## 注意事项

- Beta 版本只在 dev 分支发布
- 不需要合并到 main 分支
- 推送标签后会自动触发 GitHub Actions 构建
- Beta 版本会被标记为 "Pre-release"

## 错误处理

- 版本号格式错误：提示正确格式并重新询问
- 标签已存在：提示用户删除旧标签或使用新版本号
- 工作区不干净：提示用户先提交或暂存更改
- 不在 dev 分支：询问是否切换

