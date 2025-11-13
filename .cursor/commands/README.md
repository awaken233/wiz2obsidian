# Cursor Commands - 发版工具

本目录包含用于 wiz2obsidian 项目发版的 Cursor Commands。

## 可用命令

### `/release-beta` - 发布 Beta 版本

在 dev 分支发布 Beta 测试版本。

**使用场景：**
- 测试新功能
- 预发布版本让用户提前体验
- 验证重大变更

**工作流程：**
1. 在 Cursor 聊天框输入 `/release-beta`
2. 输入版本号（如 `v1.0.0-beta1`）
3. 命令会自动：
   - 检查版本号格式
   - 确保在 dev 分支
   - 检查工作区状态
   - 创建并推送标签
   - 触发 GitHub Actions 构建

**特点：**
- 只在 dev 分支操作
- 不需要合并到 main
- 发布为 Pre-release
- 不会显示为 Latest Release

---

### `/release-stable` - 创建发布 PR

创建从 dev 到 main 的 Pull Request，准备发布正式版本。

**使用场景：**
- 发布正式版本
- 需要 Code Review
- 需要 CI 检查

**工作流程：**
1. 在 Cursor 聊天框输入 `/release-stable`
2. 输入版本号（如 `v1.0.0`，不能有 beta 后缀）
3. 命令会自动：
   - 检查 GitHub CLI 是否安装
   - 验证版本号格式
   - 确保在 dev 分支
   - 检查工作区状态
   - 创建 PR（dev → main）
   - 自动填充 PR 描述

**后续步骤：**
1. 等待 CI 检查通过
2. 进行 Code Review（如需要）
3. 在 GitHub 上合并 PR
4. 使用 `/release-tag` 命令打标签

**前置要求：**
- 需要安装 GitHub CLI (`gh`)
  - macOS: `brew install gh`
  - 其他平台: https://cli.github.com/
- 需要认证：`gh auth login`

---

### `/release-tag` - 打标签发布

在 PR 合并到 main 后，打标签触发正式版本发布。

**使用场景：**
- PR 已经合并到 main
- 准备触发正式版本构建

**工作流程：**
1. 确保 dev → main 的 PR 已经合并
2. 在 Cursor 聊天框输入 `/release-tag`
3. 输入版本号（与创建 PR 时一致）
4. 命令会自动：
   - 切换到 main 分支
   - 拉取最新代码
   - 验证 PR 是否已合并
   - 检查标签是否存在
   - 创建并推送标签
   - 切回 dev 分支
   - 触发 GitHub Actions 构建

**注意事项：**
- 必须在 PR 合并后使用
- 标签只能在 main 分支创建
- 推送标签后会自动触发构建

---

## 完整发版流程

### Beta 版本发布

```
1. /release-beta
   ↓
2. 输入版本号（v1.0.0-beta1）
   ↓
3. 自动构建并发布为 Pre-release
```

### 正式版本发布

```
1. /release-stable
   ↓
2. 输入版本号（v1.0.0）
   ↓
3. 创建 PR（dev → main）
   ↓
4. 等待 CI 通过
   ↓
5. Code Review
   ↓
6. 合并 PR
   ↓
7. /release-tag
   ↓
8. 输入版本号（v1.0.0）
   ↓
9. 自动构建并发布为正式版本
```

---

## 版本号规则

遵循语义化版本 (Semantic Versioning)：

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| Beta 版本 | `vX.Y.Z-betaN` | `v1.0.0-beta1` | 测试版本 |
| 正式版本 | `vX.Y.Z` | `v1.0.0` | 稳定版本 |

**版本号升级规则：**
- **MAJOR (X)**: 不兼容的 API 修改
- **MINOR (Y)**: 向下兼容的功能性新增
- **PATCH (Z)**: 向下兼容的问题修正

---

## 常见问题

### Q: 发布后发现问题怎么办？

**回滚标签和 Release：**
```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
# 在 GitHub 上手动删除 Release
```

**发布修复版本：**
1. 修复代码并推送到 dev
2. 使用 `/release-stable` 创建新 PR（版本号 `v1.0.1`）
3. 合并后使用 `/release-tag` 打标签

---

## 相关文档

- [发版脚本使用说明](../../scripts/README.md)
- [发版流程文档](../../RELEASE.md)
- [GitHub CLI 文档](https://cli.github.com/manual/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)

---

**最后更新**: 2025-11-13