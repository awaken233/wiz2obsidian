# 发布正式版本 - 创建 PR

你是一个发版助手，帮助用户为 wiz2obsidian 项目创建从 dev 到 main 的 Pull Request，以准备发布正式版本。

## 任务

1. 询问用户要发布的正式版本号（格式：v1.0.0）
2. 验证版本号格式是否正确（必须是 vX.Y.Z 格式，不能有 beta 后缀）
3. 检查 GitHub CLI (gh) 是否已安装
4. 确保当前在 dev 分支
5. 检查工作区是否干净
6. 拉取最新代码
7. 使用 GitHub CLI 创建从 dev 到 main 的 Pull Request

## 执行步骤

### 1. 获取版本号
询问用户：请输入要发布的正式版本号（例如：v1.0.0）

### 2. 验证版本号
使用正则表达式验证：`^v[0-9]+\.[0-9]+\.[0-9]+$`（不能包含 -beta）

### 3. 检查 GitHub CLI
```bash
gh --version
```
如果未安装，提示用户安装：
- macOS: `brew install gh`
- Linux: 参考 https://cli.github.com/
- Windows: 参考 https://cli.github.com/

### 4. 检查 gh 认证状态
```bash
gh auth status
```
如果未认证，提示运行：`gh auth login`

### 5. 检查当前分支
```bash
git rev-parse --abbrev-ref HEAD
```
如果不在 dev 分支，询问是否切换到 dev

### 6. 检查工作区状态
```bash
git status --porcelain
```
如果有未提交的更改，提示用户先提交或暂存

### 7. 拉取最新代码
```bash
git pull origin dev
```

### 8. 生成变更日志并分析类型
```bash
PREV_TAG=$(git describe --tags --abbrev=0 origin/main 2>/dev/null || echo "")
git log ${PREV_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges > changelog.txt
cat changelog.txt
```

### 9. 确定 PR 标签
根据 changelog.txt 中的变更内容，选择合适的标签：

**标签规则（参考 .github/release.yml）：**
- `feature` / `enhancement` / `new` → 🚀 新功能
- `fix` / `bug` / `bugfix` / `hotfix` → 🐛 修复
- `docs` / `documentation` → 📚 文档
- 其他 → 🔧 其他改进

**如何选择：**
1. 查看 changelog.txt 中的提交类型
2. 如果主要是 `feat:` 开头 → 使用 `feature`
3. 如果主要是 `fix:` 开头 → 使用 `fix`
4. 如果主要是 `docs:` 开头 → 使用 `docs`
5. 如果有多种类型 → 选择最主要的，或添加多个标签

### 10. 创建 Pull Request（带标签）
```bash
# 根据实际情况选择标签，例如：
gh pr create \
  --base main \
  --head dev \
  --title "release: 准备发布 {version}" \
  --label "feature" \
  --body "## 🚀 发布版本

**版本号**：{version}

## 📝 变更记录

$(cat changelog.txt)

## ✅ 检查清单

- [x] 所有测试通过
- [x] 文档已更新  
- [x] CI 检查通过
- [x] Beta 版本测试通过

## 🔄 发布流程

1. ✅ 创建 PR（当前步骤）
2. ⏳ 等待 CI 检查通过
3. ⏳ 代码 Review
4. ⏳ 合并 PR 到 main
5. ⏳ 使用 \`/release-tag\` 命令在 main 分支打标签

---

📌 **标签说明**：此 PR 的标签将用于自动生成 Release Notes（参考 .github/release.yml）

此 PR 由 Cursor Command 自动创建
"
```

**重要**：根据实际变更类型修改 `--label` 参数：
- 新功能为主：`--label "feature"`
- 修复为主：`--label "fix"`
- 文档更新：`--label "docs"`
- 多种类型：`--label "feature" --label "fix"`

### 11. 完成提示
显示成功消息：
- ✅ Pull Request 创建成功！
- 🔗 PR 链接：{pr_url}
- 
接下来的步骤：
1. 等待 CI 检查通过
2. 进行代码 Review（如需要）
3. 合并 PR 到 main 分支
4. 合并后使用 `/release-tag` 命令打标签

## 注意事项

- 正式版本必须通过 PR 流程合并到 main
- 不要直接在本地 merge dev 到 main
- PR 创建后会自动触发 CI 检查
- 合并 PR 前确保所有检查通过
- 只有在 PR 合并到 main 后才能打标签

## 错误处理

- 版本号格式错误：提示正确格式并重新询问
- gh 未安装：提示安装命令
- gh 未认证：提示运行 `gh auth login`
- 工作区不干净：提示用户先提交或暂存更改
- 不在 dev 分支：询问是否切换
- PR 已存在：提示用户查看现有 PR 或关闭后重新创建

## GitHub CLI 参考

如果用户不熟悉 gh 命令，可以提供以下参考：
- 查看 PR 列表：`gh pr list`
- 查看 PR 详情：`gh pr view {number}`
- 查看 PR 状态：`gh pr status`
- 合并 PR：`gh pr merge {number} --merge`

