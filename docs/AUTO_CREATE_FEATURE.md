# ✨ 新功能：自动创建仓库

系统现在支持**自动检测和创建 GitHub 仓库**！

## 🚀 使用方式

配置好 `config/config.yaml` 后，直接运行：

```bash
poetry run python -m python_project
```

系统会：
1. ✅ 检测配置的仓库是否存在
2. ✅ 如果不存在，自动创建新仓库
3. ✅ 如果仓库为空，创建初始 README.md
4. ✅ 开始正常工作流程

## 📝 配置示例

```yaml
# config/config.yaml
github:
  token: ${GITHUB_TOKEN}
  repo_owner: "your-username"
  repo_name: "new-repo"  # 不存在会自动创建！
  base_branch: "main"
```

## 🧪 测试自动创建

```bash
# 验证配置和自动创建功能
poetry run python scripts/test_auto_create.py
```

## 📋 创建的仓库特性

- ✅ 公开仓库（可配置为私有）
- ✅ 启用 Issues 和 Projects
- ✅ 自动创建 README.md（如果仓库为空）
- ✅ 设置默认描述

## 🔧 禁用自动创建

如果你想手动创建仓库：

```python
from python_project.core.github_client import GitHubClient

client = GitHubClient(config.github, auto_create=False)
```

## 📚 完整文档

查看 [docs/auto_create_repo.md](docs/auto_create_repo.md) 获取：
- 详细使用说明
- 权限配置
- 故障排查
- 高级配置

---

**现在开始更简单了！** 只需配置 GitHub Token，系统会自动处理仓库创建！🚀
