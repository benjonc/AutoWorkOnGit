# GitHub 自动创建仓库功能

## ✅ 功能概述

系统现在支持**自动检测和创建 GitHub 仓库**！

### 工作原理

1. **自动检测** - 系统启动时检查配置的仓库是否存在
2. **自动创建** - 如果仓库不存在，自动创建新仓库
3. **智能初始化** - 如果仓库为空，自动创建 README.md

### 使用方式

#### 方式 1：默认自动创建（推荐）

```python
from python_project.core.config import load_config
from python_project.core.github_client import GitHubClient

config = load_config()
client = GitHubClient(config.github)  # auto_create=True by default
```

#### 方式 2：禁用自动创建

```python
client = GitHubClient(config.github, auto_create=False)
```

### 完整示例

```python
#!/usr/bin/env python3
import os
from pathlib import Path
from python_project.core.config import load_config
from python_project.core.github_client import GitHubClient

# Load config
config = load_config()

# Create client with auto-create enabled
client = GitHubClient(config.github, auto_create=True)

# Repository is now ready to use!
print(f"Repository: {client.repo.full_name}")
print(f"URL: {client.repo.html_url}")
```

## 🧪 测试

### 验证自动创建功能

```bash
# 测试现有仓库
poetry run python scripts/test_auto_create.py

# 测试创建新仓库（使用测试仓库名）
# 1. 编辑 config/config.yaml，修改 repo_name
# 2. 运行测试脚本
poetry run python scripts/test_auto_create.py
```

### 输出示例

```
============================================================
Testing Repository Auto-Create
============================================================

[INFO] Configuration:
  Owner: benjonc
  Repo: AutoWorkOnGit
  Token: ghp_FTq7JcbfbKR...

[INFO] Initializing GitHub client (auto_create=True)...

[SUCCESS] Repository ready!
  Full Name: benjonc/AutoWorkOnGit
  URL: https://github.com/benjonc/AutoWorkOnGit
  Description: Autonomous workflow system - managed by multi-agent AI
  Private: False
  Default Branch: main
  Stars: 0
  Forks: 0
```

## 📋 创建的仓库特性

自动创建的仓库包含：

- ✅ **公开仓库** (private=False)
- ✅ **启用 Issues**
- ✅ **启用 Projects**
- ✅ **启用 Wiki**
- ✅ **自动创建 README.md**（如果仓库为空）

### 自定义描述

创建的仓库会有默认描述：
> "Autonomous workflow system - managed by multi-agent AI"

## ⚙️ 配置选项

### config/config.yaml

```yaml
github:
  token: ${GITHUB_TOKEN}
  repo_owner: "your-username"
  repo_name: "your-repo-name"
  base_branch: "main"
  auto_create: true  # Optional: Control auto-creation (default: true)
```

### 环境变量

```bash
# .env.local
GITHUB_TOKEN=ghp_your_token_here
```

## 🔐 权限要求

GitHub Token 需要以下权限：

| 权限 | 用途 | 必需 |
|------|------|------|
| `repo` | 完整仓库访问 | ✅ 是 |
| `write:issues` | 创建/管理 Issues | ✅ 是 |
| `write:pull_requests` | 创建/管理 PRs | ✅ 是 |
| `public_repo` | 创建公开仓库 | ⚠️ 如果创建公开仓库 |
| `repo:status` | 更新 commit 状态 | 可选 |

### 获取 Token

1. 访问 https://github.com/settings/tokens/new
2. 选择权限：
   - ✅ `repo` (所有子选项)
   - ✅ `write:issues`
   - ✅ `write:pull_requests`
3. 点击 "Generate token"
4. 复制到 `.env.local`

## 🎯 使用场景

### 场景 1：新项目启动

```bash
# 1. 克隆项目
git clone https://github.com/your-org/AutoWorkOnGit
cd AutoWorkOnGit

# 2. 配置新仓库
cat > config/config.yaml <<EOF
github:
  token: ${GITHUB_TOKEN}
  repo_owner: "your-org"
  repo_name: "new-project"
EOF

# 3. 运行系统 - 自动创建仓库！
poetry run python -m python_project
```

### 场景 2：多环境管理

```python
# Development
dev_config = load_config("config/config.dev.yaml")
dev_client = GitHubClient(dev_config.github)

# Production
prod_config = load_config("config/config.prod.yaml")
prod_client = GitHubClient(prod_config.github)
```

### 场景 3：测试环境

```python
# 创建测试仓库
test_config = GitHubConfig(
    token=os.getenv("GITHUB_TOKEN"),
    repo_owner="your-username",
    repo_name="test-auto-workflow",
)
test_client = GitHubClient(test_config, auto_create=True)
```

## ⚠️ 注意事项

### 1. 仓库已存在

如果仓库已存在，系统会：
- ✅ 检测到现有仓库
- ✅ 直接使用，不创建新的
- ✅ 记录日志：`Repository found: owner/repo`

### 2. 权限不足

如果 Token 没有创建仓库的权限：
- ❌ 抛出异常：`Permission denied`
- 💡 解决方案：确保 Token 有 `repo` 权限

### 3. 组织仓库

为组织创建仓库需要：
- Token 有组织权限
- 你是该组织的成员

### 4. 仓库名冲突

如果仓库名已被占用：
- ❌ GitHub API 会返回 422 错误
- 💡 解决方案：选择不同的仓库名

## 📊 监控和日志

### 日志级别

```python
import logging

# 设置详细日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("python_project.core.github_client")
logger.setLevel(logging.DEBUG)
```

### 日志输出示例

```
[INFO] Authenticated as GitHub user: benjonc
[WARNING] Repository not found: benjonc/NewRepo
[INFO] Creating new repository...
[INFO] Repository created: benjonc/NewRepo
[INFO] Repository is empty, creating initial commit...
[INFO] Created README.md with initial commit
```

## 🔧 高级配置

### 禁用自动创建

```python
# 方式 1：构造函数参数
client = GitHubClient(config.github, auto_create=False)

# 方式 2：配置文件
# config/config.yaml
github:
  auto_create: false
```

### 自定义初始内容

编辑 `github_client.py` 中的 `_ensure_default_branch` 方法：

```python
def _ensure_default_branch(self, repo):
    """Customize initial commit content."""
    custom_readme = f"""# {repo.name}

Custom description here.

## Features
- Feature 1
- Feature 2

## Getting Started
Instructions here.
"""
    repo.create_file(
        path="README.md",
        message="Initial commit",
        content=custom_readme,
        branch="main",
    )
```

## 🐛 故障排查

### 问题 1：认证失败

```
GitHub authentication failed. Please check your GITHUB_TOKEN.
```

**解决方案**：
1. 检查 `.env.local` 中的 `GITHUB_TOKEN`
2. 验证 Token 未过期
3. 确认 Token 有正确权限

### 问题 2：仓库创建失败

```
Failed to create repository: Permission denied
```

**解决方案**：
1. 确保 Token 有 `repo` 权限
2. 检查用户/组织名称正确
3. 验证你有所需的组织权限

### 问题 3：仓库已存在但检测失败

```
Repository not found: owner/repo
```

**解决方案**：
1. 检查 `repo_owner` 和 `repo_name` 拼写
2. 验证你有访问该仓库的权限
3. 检查是否为私有仓库（需要 `repo` 权限）

## 📚 相关文档

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [SETUP_GUIDE.md](../SETUP_GUIDE.md) - 完整设置指南
- [docs/api.md](api.md) - API 参考

---

**功能已完全集成！** 系统现在可以自动管理仓库，无需手动创建。🚀
