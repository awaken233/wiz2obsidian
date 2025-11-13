# 发布正式版本 - 打标签

你是一个发版助手，帮助用户在 PR 合并到 main 后打标签并触发正式版本发布。

## 前置条件

⚠️ **重要**：此命令只能在以下情况使用：
1. dev 到 main 的 PR 已经创建（使用 `/release-stable` 命令创建）
2. PR 已经通过所有 CI 检查
3. PR 已经完成 Code Review
4. PR 已经成功合并到 main 分支

如果 PR 还未合并，请先完成 PR 合并流程。

## 任务

1. 询问用户版本号（应该与之前创建 PR 时使用的版本号一致）
2. 验证版本号格式
3. 确认当前在 main 分支
4. 拉取最新的 main 分支代码
5. 检查标签是否已存在
6. 创建并推送标签

## 执行步骤

### 1. 获取版本号
询问用户：请输入要发布的版本号（例如：v1.0.0）

### 2. 验证版本号
使用正则表达式验证：`^v[0-9]+\.[0-9]+\.[0-9]+$`

### 3. 检查当前分支
```bash
git rev-parse --abbrev-ref HEAD
```
如果不在 main 分支，提示：
- ⚠️ 当前不在 main 分支
- 正式版本的标签必须在 main 分支创建
- 是否切换到 main 分支？

### 4. 切换到 main 并拉取最新代码
```bash
git checkout main
git pull origin main
```

### 5. 验证 PR 是否已合并
```bash
git log --oneline -10
```
检查最近的提交记录，确认是否有 "release: 准备发布 {version}" 的合并提交

如果没有找到，警告用户：
- ⚠️ 未找到对应的发布合并提交
- 请确认 dev 到 main 的 PR 是否已经合并
- 是否继续打标签？

### 6. 检查标签是否存在
```bash
git tag -l | grep "^{version}$"
```
如果标签已存在，提示：
- ❌ 标签 {version} 已存在
- 如需重新发布，请先删除标签：
  ```bash
  git tag -d {version}
  git push origin :refs/tags/{version}
  ```

### 7. 创建并推送标签
```bash
git tag {version}
git push origin {version}
```

### 8. 切回 dev 分支
```bash
git checkout dev
```

### 9. 完成提示
显示成功消息：
- ✅ 正式版本 {version} 标签创建成功！
- 🔗 查看构建进度：https://github.com/{repo}/actions
- 🔗 查看发布页面：https://github.com/{repo}/releases/tag/{version}
- 
发布流程：
1. ✅ 创建 PR（已完成）
2. ✅ CI 检查通过（已完成）
3. ✅ 代码 Review（已完成）
4. ✅ 合并 PR 到 main（已完成）
5. ✅ 创建版本标签（刚刚完成）
6. ⏳ GitHub Actions 正在构建发布包...

预计 10-15 分钟后可在 Releases 页面下载各平台的安装包。

## 注意事项

- 标签必须在 main 分支创建
- 确保 PR 已经合并到 main
- 推送标签后会自动触发 GitHub Actions 构建
- 构建完成后会自动创建 Release
- Release 会包含所有平台的可执行文件

## 错误处理

- 版本号格式错误：提示正确格式
- 不在 main 分支：提示切换到 main
- 标签已存在：提示删除旧标签的命令
- PR 未合并：警告并询问是否继续
- 推送失败：检查网络和权限

## 完整发布流程回顾

### Beta 版本发布（在 dev 分支）
1. 使用 `/release-beta` 命令
2. 输入版本号（如 v1.0.0-beta1）
3. 自动创建并推送标签
4. GitHub Actions 自动构建并发布为 Pre-release

### 正式版本发布（dev → main）
1. 使用 `/release-stable` 命令创建 PR
2. 等待 CI 检查通过
3. 进行 Code Review
4. 在 GitHub 上合并 PR 到 main
5. 使用 `/release-tag` 命令打标签（当前命令）
6. GitHub Actions 自动构建并发布为正式版本

## 回滚操作

如果发布后发现严重问题，可以：

1. 删除标签和 Release
```bash
git tag -d {version}
git push origin :refs/tags/{version}
# 然后在 GitHub 上手动删除 Release
```

2. 修复问题后重新发布修订版本
```bash
# 修复代码并推送到 dev
# 创建新的 PR 合并到 main
# 使用新版本号（如 v1.0.1）重新打标签
```

