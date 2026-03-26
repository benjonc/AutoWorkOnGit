# 🚀 快速设置指南

## ⚠️ 运行前必须完成

### 1. 创建配置文件

```bash
# 复制示例配置
cp config/config.yaml.example config/config.yaml

# 或者直接复制这个模板
```

### 2. 编辑 config/config.yaml

```yaml
github:
  token: ${GITHUB_TOKEN}  # 从环境变量读取
  repo_owner: "你的GitHub用户名"
  repo_name: "你的仓库名称"
  base_branch: "main"

claude:
  api_key: ${ANTHROPIC_API_KEY}  # 从环境变量读取
  model: "claude-sonnet-4-6"
  headless_timeout: 600
```

### 3. 设置环境变量

创建 `.env.local` 文件：

```bash
# .env.local
GITHUB_TOKEN=ghp_your_token_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

#### 获取密钥

**GitHub Token:**
1. 访问 https://github.com/settings/tokens
2. Generate new token (classic)
3. 选择权限：`repo`, `write:issues`, `write:pull_requests`
4. 复制生成的token

**Anthropic API Key:**
1. 访问 https://console.anthropic.com/
2. API Keys → Create Key
3. 复制生成的key

### 4. 运行

```bash
# 激活环境
poetry shell

# 运行工作流
python -m python_project

# 或者直接运行
poetry run python -m python_project
```

## ✅ 验证安装

```bash
# 运行测试
poetry run pytest

# 检查代码质量
poetry run black --check src
poetry run ruff check src
```

## 📝 常见问题

### Q: 提示 "No module named python_project"
A: 确保在项目根目录运行，并且已经运行 `poetry install`

### Q: 提示 "Config file not found"
A: 需要创建 `config/config.yaml` 文件

### Q: 提示 "GitHub API authentication failed"
A: 检查 GITHUB_TOKEN 是否正确设置

### Q: 提示 "Anthropic API key invalid"
A: 检查 ANTHROPIC_API_KEY 是否正确设置

## 🎯 下一步

1. 阅读 [快速开始指南](docs/quickstart.md)
2. 查看 [使用案例](docs/examples.md)
3. 了解 [系统架构](docs/architecture.md)

---
**需要帮助?** 查看 [完整文档](docs/) 或提交 Issue
