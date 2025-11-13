# 发版流程文档

本文档详细说明了 wiz2obsidian 项目的版本发布流程，包括问题修复、预发布版本和正式发布版本的完整操作指南。

## 目录

- [分支说明](#分支说明)
- [Issue 处理流程](#issue-处理流程)
- [版本发布流程](#版本发布流程)
  - [预发布版本（Beta）](#预发布版本beta)
  - [正式版本](#正式版本)
- [自动化脚本](#自动化脚本)
- [工作流说明](#工作流说明)
- [常见问题](#常见问题)

---

## 分支说明

项目采用以下分支策略：

- **`main`** - 主分支，存放稳定的生产代码，只接受来自 dev 的 PR
- **`dev`** - 开发分支，日常开发和 bug 修复都在此分支进行
- **`feature/*`** - 功能分支（可选），用于开发大型新功能
- **`hotfix/*`** - 热修复分支（可选），用于紧急修复生产问题

---

## Issue 处理流程

### 1. 收到 Issue 后的标准流程

#### 步骤 1: 在 dev 分支创建修复分支

```bash
# 切换到 dev 分支并更新
git checkout dev
git pull origin dev

# 创建修复分支（可选，也可以直接在 dev 上修改）
git checkout -b fix/issue-123-description
```

#### 步骤 2: 进行代码修复

```bash
# 修改代码...
# 运行测试确保修复有效

# 提交修改
git add .
git commit -m "fix: 修复 issue #123 的问题描述"
```

#### 步骤 3: 推送到远程并创建 Pull Request

```bash
# 推送到远程
git push origin fix/issue-123-description

# 在 GitHub 上创建 PR:
# - 源分支: fix/issue-123-description
# - 目标分支: dev
# - 标题: fix: 修复 issue #123 的问题描述
# - 描述: 详细说明修复内容，关联 issue (#123)
```

#### 步骤 4: PR 审核和合并

```bash
# 审核通过后，在 GitHub 上合并 PR 到 dev
# 可以选择 "Squash and merge" 保持历史整洁

# 合并后删除修复分支
git branch -d fix/issue-123-description
git push origin --delete fix/issue-123-description
```

### 2. 简化流程（直接在 dev 开发）

如果是小修改，可以直接在 dev 分支操作：

```bash
git checkout dev
git pull origin dev

# 修改代码
git add .
git commit -m "fix: 修复某个问题"
git push origin dev
```

---

## 版本发布流程

### 预发布版本（Beta）

预发布版本用于测试新功能或重大修复，让用户提前体验并反馈问题。

#### 手动发布 Beta 版本

```bash
# 1. 确保 dev 分支是最新的
git checkout dev
git pull origin dev

# 2. 创建 beta 版本标签
git tag v1.0.0-beta1
git push origin v1.0.0-beta1

# 3. GitHub Actions 会自动触发构建和发布
# 查看进度：https://github.com/你的用户名/wiz2obsidian/actions
```

#### Beta 版本命名规则

- `v1.0.0-beta1` - 第一个 beta 版本
- `v1.0.0-beta2` - 第二个 beta 版本
- `v1.2.3-beta1` - 版本 1.2.3 的第一个 beta

#### Beta 版本特点

- 会标记为 "Pre-release"（预发布）
- 不会作为 "Latest Release" 展示
- 用户可以选择下载测试
- 自动构建所有平台（Windows、macOS、Linux）

---

### 正式版本

当 dev 分支的代码经过充分测试后，可以发布正式版本。

#### 方法 1: 手动发布（推荐用于理解流程）

```bash
# 1. 将 dev 分支合并到 main
git checkout main
git pull origin main
git merge dev
git push origin main

# 2. 在 main 分支创建版本标签
git tag v1.0.0
git push origin v1.0.0

# 3. GitHub Actions 自动构建和发布
```

#### 方法 2: 通过 PR 合并（推荐用于团队协作）

```bash
# 1. 创建从 dev 到 main 的 PR
# 在 GitHub 上操作:
# - 源分支: dev
# - 目标分支: main
# - 标题: release: 准备发布 v1.0.0

# 2. 审核并合并 PR

# 3. 在 main 分支打标签
git checkout main
git pull origin main
git tag v1.0.0
git push origin v1.0.0
```

#### 版本号规则（语义化版本）

遵循 [Semantic Versioning 2.0.0](https://semver.org/lang/zh-CN/)：

- **主版本号（MAJOR）**: 不兼容的 API 修改，如 `v2.0.0`
- **次版本号（MINOR）**: 向下兼容的功能性新增，如 `v1.1.0`
- **修订号（PATCH）**: 向下兼容的问题修正，如 `v1.0.1`

示例：
- `v1.0.0` → `v1.0.1` - bug 修复
- `v1.0.1` → `v1.1.0` - 新增功能
- `v1.9.0` → `v2.0.0` - 重大变更

---

## 使用 Cursor Commands 发版

项目使用 Cursor Commands 进行版本发布，提供了简单、安全的发版流程。

### Beta 版本发布

在 Cursor IDE 聊天框输入：
```
/release-beta
```

然后输入版本号（如 `v1.0.0-beta1`），命令会自动：
1. 检查版本号格式
2. 确保在 dev 分支
3. 检查工作区状态
4. 创建并推送标签
5. 触发 GitHub Actions 构建

### 正式版本发布

**步骤 1：创建 PR**

在 Cursor IDE 聊天框输入：
```
/release-stable
```

输入版本号（如 `v1.0.0`），命令会：
1. 检查 GitHub CLI 是否安装
2. 验证版本号格式
3. 创建 dev → main 的 Pull Request
4. 自动填充 PR 描述

**步骤 2：等待 PR 合并**
- CI 检查通过
- Code Review（如需要）
- 在 GitHub 上合并 PR

**步骤 3：打标签发布**

PR 合并后，在 Cursor IDE 聊天框输入：
```
/release-tag
```

输入版本号（与 PR 一致），命令会：
1. 切换到 main 分支
2. 拉取最新代码
3. 创建并推送标签
4. 触发 GitHub Actions 构建

### 详细说明

更多信息请查看：
- [Cursor Commands 使用说明](.cursor/commands/README.md)

---

## 工作流说明

项目配置了以下 GitHub Actions 工作流：

### 1. 正式版本发布 (`.github/workflows/build_and_release.yml`)

**触发条件：** 推送 `v*` 格式的标签（如 `v1.0.0`）

**执行流程：**
1. 在 4 个平台并行构建可执行文件：
   - Windows (`.exe`)
   - macOS ARM64 (Apple Silicon)
   - macOS Intel (x86_64)
   - Linux
2. 下载所有构建产物
3. 打包成带版本号的 zip 文件
4. 创建 GitHub Release
5. 自动生成 Release Notes
6. 上传所有平台的安装包

**产物命名：**
- `wiz2obsidian-v1.0.0-Windows.zip`
- `wiz2obsidian-v1.0.0-MacOS-ARM64.zip`
- `wiz2obsidian-v1.0.0-MacOS-Intel.zip`
- `wiz2obsidian-v1.0.0-Linux.zip`

### 2. 预发布版本 (`.github/workflows/prerelease.yml`)

**触发条件：** 推送 `v*-beta*` 格式的标签（如 `v1.0.0-beta1`）

**与正式版本的区别：**
- 标记为 `prerelease: true`
- 不会显示为 "Latest Release"
- 其他流程完全一致

### 3. 自动关闭不活跃 Issue (`.github/workflows/stale.yml`)

**触发条件：** 每天北京时间凌晨 1:30 运行

**功能：**
- 30 天无活动的 issue 标记为 `stale`
- 标记后 14 天仍无响应则自动关闭
- 不处理 Pull Request

---

## 常见问题

### Q1: 如何撤销已发布的版本？

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0

# 在 GitHub 上手动删除对应的 Release
```

### Q2: 发版后发现严重 bug 怎么办？

**紧急修复流程：**

```bash
# 1. 在 dev 分支快速修复
git checkout dev
# ... 修复代码 ...
git commit -m "fix: 紧急修复严重bug"
git push origin dev

# 2. 立即发布修订版本
./scripts/release.sh v1.0.1
```

### Q3: 如何只构建特定平台？

修改对应的 workflow 文件，注释掉不需要的构建任务。

### Q4: Beta 版本测试通过后，如何升级为正式版本？

```bash
# Beta 版本: v1.0.0-beta1
# 正式版本: v1.0.0

# 只需在 main 分支打新标签
git checkout main
git pull origin main
git merge dev
git push origin main
git tag v1.0.0
git push origin v1.0.0
```

### Q5: 可以跳过某个版本号吗？

可以。版本号只是一个标记，但建议遵循语义化版本规范保持一致性。

### Q6: 如何查看某个版本对应的代码？

```bash
# 查看标签对应的提交
git show v1.0.0

# 切换到该版本的代码
git checkout v1.0.0

# 切回最新代码
git checkout dev  # 或 main
```

---

## 最佳实践

### 1. 版本发布检查清单

发布前确认：
- [ ] 所有测试通过
- [ ] README 和文档已更新
- [ ] CHANGELOG 已更新（如果有）
- [ ] 版本号符合语义化版本规范
- [ ] 已在本地测试构建的可执行文件
- [ ] 重要变更已通知相关人员

### 2. Beta 测试建议

- 重大功能变更建议至少发布 1 个 beta 版本
- Beta 版本应保持至少 3-7 天供用户测试
- 收集用户反馈后再发布正式版本

### 3. 发版节奏

- **Patch 版本**: 发现 bug 后尽快修复发布
- **Minor 版本**: 累积 2-3 个新功能后发布
- **Major 版本**: 重大重构或不兼容变更时发布

### 4. Commit 规范

使用约定式提交（Conventional Commits）：

```
feat: 新增功能
fix: 修复 bug
docs: 文档修改
style: 代码格式调整
refactor: 重构
perf: 性能优化
test: 测试相关
chore: 构建/工具链
ci: CI/CD 相关
```

---

## 快速参考

### 使用 Cursor Commands（推荐）

```
# Beta 版本
/release-beta → 输入 v1.0.0-beta1

# 正式版本
/release-stable → 输入 v1.0.0 → 等待 PR 合并 → /release-tag → 输入 v1.0.0
```

### 手动操作

```bash
# 发布 Beta 版本（在 dev 分支）
git checkout dev
git pull origin dev
git tag v1.0.0-beta1
git push origin v1.0.0-beta1

# 发布正式版本（通过 PR）
gh pr create --base main --head dev --title "release: v1.0.0"
# 等待 PR 合并
git checkout main
git pull origin main
git tag v1.0.0
git push origin v1.0.0
```

---

## 相关链接

- [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)
- [约定式提交](https://www.conventionalcommits.org/zh-hans/)
- [GitHub Actions 文档](https://docs.github.com/cn/actions)
- [PyInstaller 文档](https://pyinstaller.org/)

---

**最后更新**: 2025-11-12

