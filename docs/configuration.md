# 配置指南

本文档详细说明系统的所有配置选项。

## 📁 配置文件位置

```
config/
└── config.yaml  # 主配置文件
```

## ⚙️ 配置项说明

### GitHub配置

```yaml
github:
  # GitHub Personal Access Token (必填)
  # 从环境变量 GITHUB_TOKEN 读取
  token: ${GITHUB_TOKEN}

  # 仓库所有者 (必填)
  repo_owner: "your-username"

  # 仓库名称 (必填)
  repo_name: "your-repo"

  # 基础分支，用于创建PR的目标分支
  base_branch: "main"  # 或 "master", "develop"

  # GitHub API基础URL (可选)
  # 用于GitHub Enterprise
  api_base_url: "https://api.github.com"
```

### Claude配置

```yaml
claude:
  # Anthropic API Key (必填)
  # 从环境变量 ANTHROPIC_API_KEY 读取
  api_key: ${ANTHROPIC_API_KEY}

  # 使用的Claude模型
  model: "claude-sonnet-4-6"

  # 无头模式超时时间 (秒)
  # 建议: 300-900秒
  headless_timeout: 600

  # 最大重试次数
  max_retries: 3

  # 温度参数 (0-1)
  # 较低的值更确定，较高的值更随机
  temperature: 0.7
```

### 分支策略配置

```yaml
branch_strategy:
  # 分支命名模板
  # 可用变量: {agent_type}, {issue_id}, {slug}
  prefix_template: "agent/{agent_type}/{issue_id}"

  # 最大并行Agent数量
  # 建议: 3-10
  max_parallel_agents: 5

  # 自动清理已合并的分支
  auto_cleanup: true

  # 分支保护规则
  protection:
    # 禁止强制推送
    no_force_push: true

    # 禁止删除未合并的分支
    no_delete_unmerged: true
```

### 工作空间配置

```yaml
workspace_root: "."  # 项目根目录

docs_dir: "docs"  # 文档目录

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARN, ERROR
  format: "json"  # text, json
  file: "logs/workflow.log"
```

### Agent配置

```yaml
agents:
  # 需求收集Agent
  requirements_collector:
    enabled: true
    max_questions: 20  # 最多询问用户的问题数

  # 任务分析Agent
  task_analyzer:
    enabled: true
    max_task_depth: 3  # 任务拆分最大深度

  # 代码执行Agent
  code_executor:
    enabled: true
    test_command: "pytest"  # 测试命令
    lint_command: "ruff check"  # 代码检查命令

  # PR审核Agent
  pr_reviewer:
    enabled: true
    auto_approve: false  # 是否自动批准
    required_approvals: 1  # 需要的审核数量
```

### 执行策略配置

```yaml
execution:
  # 失败处理策略
  failure_strategy: "retry"  # retry, skip, abort

  # 重试配置
  retry:
    max_attempts: 3
    backoff_factor: 2  # 指数退避因子
    initial_delay: 4  # 初始延迟(秒)

  # 超时配置
  timeout:
    task: 600  # 单个任务超时(秒)
    phase: 3600  # 阶段超时(秒)
    workflow: 86400  # 完整工作流超时(秒)
```

### 通知配置

```yaml
notifications:
  # 邮件通知
  email:
    enabled: false
    smtp_host: "smtp.example.com"
    smtp_port: 587
    from_address: "noreply@example.com"

  # Slack通知
  slack:
    enabled: false
    webhook_url: ${SLACK_WEBHOOK_URL}
    channel: "#dev-updates"

  # GitHub通知
  github:
    enabled: true
    comment_on_issues: true
    comment_on_prs: true
```

## 🎨 高级配置

### 自定义Agent行为

```yaml
custom_agents:
  # 自定义需求模板
  requirements_template: |
    # 需求文档

    ## 项目概述
    {project_overview}

    ## 功能需求
    {functional_requirements}

  # 自定义任务模板
  task_template: |
    ## 任务描述
    {description}

    ## 验收标准
    {acceptance_criteria}
```

### 性能调优

```yaml
performance:
  # 缓存配置
  cache:
    enabled: true
    ttl: 300  # 缓存过期时间(秒)
    max_size: 100  # 最大缓存数量

  # 并发控制
  concurrency:
    semaphore_limit: 10  # 信号量限制
    rate_limit: 100  # API调用速率限制(次/分钟)

  # 批量操作
  batch:
    size: 10  # 批量操作大小
    delay: 1  # 批次间延迟(秒)
```

### 安全配置

```yaml
security:
  # API密钥加密
  encrypt_secrets: true

  # 审计日志
  audit_log:
    enabled: true
    file: "logs/audit.log"

  # 权限控制
  permissions:
    # 只允许特定Agent执行特定操作
    code_executor:
      - "create_file"
      - "modify_file"
      - "run_tests"
    pr_reviewer:
      - "review_pr"
      - "approve_pr"
      - "reject_pr"
```

## 📝 环境变量

### 必需的环境变量

```bash
# .env.local
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

### 可选的环境变量

```bash
# 日志级别
LOG_LEVEL=INFO

# 工作流ID (覆盖自动生成)
WORKFLOW_RUN_ID=custom-run-001

# 禁用颜色输出
NO_COLOR=1

# 调试模式
DEBUG=1

# 配置文件路径 (覆盖默认)
CONFIG_PATH=/path/to/custom/config.yaml
```

## 🔄 配置验证

### 启动时验证

系统启动时会自动验证配置:

```python
from python_project.core.config import load_config

try:
    config = load_config()
    print("✅ 配置有效")
except Exception as e:
    print(f"❌ 配置错误: {e}")
```

### 验证规则

| 配置项 | 验证规则 |
|--------|---------|
| `github.token` | 必须是有效的GitHub Token格式 |
| `github.repo_owner` | 不能为空 |
| `github.repo_name` | 不能为空 |
| `claude.api_key` | 必须以 `sk-ant-` 开头 |
| `claude.model` | 必须是有效的Claude模型名 |
| `branch_strategy.max_parallel_agents` | 1-20之间 |

## 🌍 环境特定配置

### 开发环境

```yaml
# config/config.development.yaml
logging:
  level: DEBUG

execution:
  timeout:
    task: 300

branch_strategy:
  auto_cleanup: true
```

### 生产环境

```yaml
# config/config.production.yaml
logging:
  level: INFO

execution:
  timeout:
    task: 900

branch_strategy:
  auto_cleanup: false

notifications:
  slack:
    enabled: true
```

### 测试环境

```yaml
# config/config.test.yaml
github:
  repo_name: "test-repo"

execution:
  failure_strategy: "skip"

branch_strategy:
  max_parallel_agents: 2
```

## 🔧 配置覆盖优先级

配置按以下优先级加载(从低到高):

1. `config/config.yaml` (基础配置)
2. `config/config.{environment}.yaml` (环境特定配置)
3. 环境变量 (最高优先级)

示例:

```bash
# 基础配置: max_parallel_agents = 5
# 环境配置: max_parallel_agents = 3
# 环境变量: MAX_PARALLEL_AGENTS=7

# 最终值: 7 (环境变量优先级最高)
```

## 📊 配置示例

### 小型项目配置

```yaml
github:
  repo_owner: "myuser"
  repo_name: "small-project"
  base_branch: "main"

claude:
  model: "claude-sonnet-4-6"
  headless_timeout: 300

branch_strategy:
  max_parallel_agents: 3

execution:
  timeout:
    workflow: 3600  # 1小时
```

### 大型项目配置

```yaml
github:
  repo_owner: "myorg"
  repo_name: "large-project"
  base_branch: "develop"

claude:
  model: "claude-opus-4-6"
  headless_timeout: 900

branch_strategy:
  max_parallel_agents: 10

execution:
  timeout:
    workflow: 86400  # 24小时

performance:
  cache:
    enabled: true
```

---

**下一步**: 查看 [快速开始指南](./quickstart.md) 开始使用系统
