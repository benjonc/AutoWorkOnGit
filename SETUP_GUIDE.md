# 🔧 配置设置指南

## ❌ 当前错误：GitHub 认证失败

你看到的错误：
```
github.GithubException.BadCredentialsException: 401 {"message": "Bad credentials"}
```

这表示 GitHub Token 无效或未正确配置。

## ✅ 解决方案（3步）

### Step 1: 获取 GitHub Token

1. 访问 https://github.com/settings/tokens/new
2. 填写信息：
   - **Note**: "AutoWorkOnGit"
   - **Expiration**: 选择 "No expiration" 或你想要的时长
   - **Scopes**: 勾选以下权限
     - ✅ `repo` (完整仓库访问)
     - ✅ `write:issues` (创建和管理 Issues)
     - ✅ `write:pull_requests` (创建和管理 PRs)

3. 点击 "Generate token"
4. **立即复制 token**（只显示一次！）
   - 格式类似: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: 创建环境变量文件

在项目根目录创建 `.env.local` 文件：

```bash
# .env.local
GITHUB_TOKEN=ghp_你刚才复制的token
ANTHROPIC_API_KEY=sk-ant-你的API密钥
```

#### 获取 Anthropic API Key

1. 访问 https://console.anthropic.com/
2. 登录/注册
3. 进入 "API Keys" 页面
4. 点击 "Create Key"
5. 复制生成的密钥
   - 格式类似: `sk-ant-xxxxxx`

### Step 3: 更新配置文件

编辑 `config/config.yaml`：

```yaml
github:
  token: ${GITHUB_TOKEN}
  repo_owner: "你的GitHub用户名"  # 不是邮箱！
  repo_name: "你的仓库名称"       # 例如: AutoWorkOnGit
  base_branch: "main"
```

**重要提示**:
- `repo_owner` 是你的 GitHub 用户名，不是邮箱
- `repo_name` 是仓库名称，不是完整URL
- 例如: 用户名 `johnsmith`, 仓库 `my-project`

## 🧪 验证配置

运行配置验证脚本：

```bash
# 这会自动加载 .env.local
poetry run python scripts/validate_config.py
```

预期输出：
```
============================================================
Python Project - Configuration Validator
============================================================

1. Checking environment variables...
   ✓ GITHUB_TOKEN: ghp_abcd...wxyz
   ✓ ANTHROPIC_API_KEY: sk-ant-abcd...wxyz

2. Checking configuration file...
   ✓ Config file found: config\config.yaml
   ✓ github.repo_owner: your-actual-username
   ✓ github.repo_name: your-actual-repo

3. Testing GitHub connection...
   ✓ Authenticated as: your-actual-username
   ✓ Repository accessible: your-actual-username/your-actual-repo

4. Testing Claude API...
   ✓ API key is set (not testing actual API call)

============================================================
Summary:
============================================================
✓ PASS: Environment Variables
✓ PASS: Configuration File
✓ PASS: GitHub Connection
✓ PASS: Claude API
============================================================

✓ All checks passed! You're ready to run:
  poetry run python -m python_project
```

## 🚀 再次运行

配置完成后：

```bash
# 方法1: 直接运行（推荐）
poetry run python -m python_project

# 方法2: 激活环境后运行
poetry shell
python -m python_project
```

## 📋 完整配置示例

### .env.local
```bash
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### config/config.yaml
```yaml
github:
  token: ${GITHUB_TOKEN}
  repo_owner: "johndoe"          # 你的GitHub用户名
  repo_name: "my-awesome-project" # 你的仓库名
  base_branch: "main"

claude:
  api_key: ${ANTHROPIC_API_KEY}
  model: "claude-sonnet-4-6"
  headless_timeout: 600

branch_strategy:
  max_parallel_agents: 5
  auto_cleanup: true

workspace_root: "."
docs_dir: "docs"
```

## 🔒 安全提示

- ✅ **.env.local 已经在 .gitignore 中** - 不会被提交
- ✅ **永远不要提交真实的 token**
- ✅ **使用环境变量而不是硬编码密钥**
- ✅ **定期更换你的 token**

## ❓ 常见问题

### Q1: Token 权限错误
```
403 {"message": "Resource not accessible by integration"}
```
**解决**: 确保 token 有 `repo` 权限

### Q2: 仓库未找到
```
404 {"message": "Not Found"}
```
**解决**:
- 检查 `repo_owner` 是否正确（用户名，不是邮箱）
- 检查 `repo_name` 是否正确
- 确保你有权限访问这个仓库

### Q3: 环境变量未加载
**解决**: 确保 `.env.local` 在项目根目录（和 `pyproject.toml` 同级）

## 📞 需要帮助？

1. 运行 `poetry run python scripts/validate_config.py` 查看详细错误
2. 检查 [GitHub Token 设置](https://github.com/settings/tokens)
3. 检查 [Anthropic API Key 设置](https://console.anthropic.com/)

---

**配置正确后，系统就可以正常运行了！** 🎉
