# Autonomous Workflow System for Claude Code

🤖 **多Agent协作的自动化工作流系统** - 使用Claude Code无头模式自动完成从需求收集到PR合并的完整流程

## ⚡ 快速开始（3步）

### 1️⃣ 配置环境变量

```bash
# 复制模板
cp .env.example .env.local

# 编辑 .env.local，填入你的密钥：
GITHUB_TOKEN=ghp_你的token
ANTHROPIC_API_KEY=sk-ant-你的key
```

**获取密钥**:
- GitHub Token: https://github.com/settings/tokens/new (需要 `repo`, `write:issues`, `write:pull_requests` 权限)
- Anthropic API Key: https://console.anthropic.com/

### 2️⃣ 配置仓库信息

编辑 `config/config.yaml`:

```yaml
github:
  repo_owner: "你的GitHub用户名"  # 不是邮箱！
  repo_name: "你的仓库名称"
```

### 3️⃣ 验证并运行

```bash
# 验证配置
poetry run python scripts/validate_config.py

# 运行系统
poetry run python -m python_project
```

## 📖 详细指南

- 🔧 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 完整配置指南（解决认证错误）
- 🚀 **[GETTING_STARTED.md](GETTING_STARTED.md)** - 新手入门
- 📚 **[docs/quickstart.md](docs/quickstart.md)** - 5分钟快速开始

## ❌ 遇到问题？

### 认证错误 (401 Bad credentials)

```
github.GithubException.BadCredentialsException: 401 {"message": "Bad credentials"}
```

**解决方案**: 查看 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** 获取详细步骤

### 配置验证

运行配置验证器查看具体问题：

```bash
poetry run python scripts/validate_config.py
```

## 🎯 系统特性

| 特性 | 说明 |
|------|------|
| **完整自动化流程** | 需求收集→任务拆分→并行执行→审核→合并 |
| **多Agent协作** | 最多5个Agent同时工作，依赖感知调度 |
| **智能分支管理** | 自动命名、冲突避免、自动清理 |
| **自动代码审核** | 6维度检查（质量/测试/安全/性能/文档/架构） |
| **容错恢复** | 自动重试、状态持久化 |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Workflow Orchestrator                      │
│              (协调完整工作流执行)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
      ┌───────────────┴──────────────┐
      │                              │
┌─────▼──────┐               ┌──────▼─────┐
│  Agents    │               │   Core     │
├────────────┤               ├────────────┤
│• Req Coll. │◄──────────────┤• GitHub    │
│• Task An.  │               │  Client    │
│• PR Review │               │• Claude    │
│• Code Exec │               │  Executor  │
└────────────┘               │• Config    │
                             └────────────┘
```

### Agent类型

1. **RequirementsCollectorAgent** - 需求收集Agent
   - 与用户对话收集需求
   - 生成结构化需求文档
   - 识别技术约束和成功标准

2. **TaskAnalyzerAgent** - 任务分析Agent
   - 拆分需求为原子任务
   - 构建任务依赖图
   - 识别并行执行机会

3. **CodeExecutionAgent** - 代码执行Agent
   - 使用Claude Code无头模式
   - 自动实现功能
   - 编写测试和文档

4. **PRReviewAgent** - PR审核Agent
   - 自动化代码审核
   - 检查代码质量和安全
   - 生成修复建议

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Poetry 2.0+
- GitHub Personal Access Token
- Anthropic API Key

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/autonomous-workflow.git
cd autonomous-workflow

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 配置

1. **设置环境变量**

```bash
# 创建 .env 文件
cat > .env <<EOF
GITHUB_TOKEN=ghp_xxxx
ANTHROPIC_API_KEY=sk-ant-xxxx
EOF
```

2. **修改配置文件**

编辑 `config/config.yaml`:

```yaml
github:
  repo_owner: "your-username"
  repo_name: "your-repo"
  base_branch: "main"

claude:
  model: "claude-sonnet-4-6"
  headless_timeout: 600
```

### 运行

```bash
# 运行完整工作流
poetry run python -m python_project.main
```

## 📖 工作流详解

### Phase 1: 需求收集

```
用户输入 → RequirementsCollectorAgent → requirements.md
```

- 交互式对话
- 结构化整理
- 生成需求文档

### Phase 2: 任务拆分与依赖分析

```
requirements.md → TaskAnalyzerAgent → task_breakdown.yaml
```

- 拆分为原子任务
- 构建依赖图
- 计算执行阶段

### Phase 3: GitHub Issue管理

```
task_breakdown.yaml → GitHub Issues + issues/*.md
```

- 创建对应Issues
- 生成Issue文档
- 设置标签和里程碑

### Phase 4: 并行任务执行

```
┌─ Agent 1 → Issue #1 → Branch → PR #10 ─┐
├─ Agent 2 → Issue #2 → Branch → PR #11 ─┤
├─ Agent 3 → Issue #3 → Branch → PR #12 ─┤
└─ Agent 4 → Issue #4 → Branch → PR #13 ─┘
                │
                ▼
        Parallel Execution
        (Max: config.branch_strategy.max_parallel_agents)
```

### Phase 5: PR审核

```
PR → PRReviewAgent → Review Result
              │
              ├─ Approved → Ready for Merge
              │
              └─ Changes Requested → Fix Issues
                     │
                     └─> CodeExecutionAgent → Fix PR
```

### Phase 6: 合并与清理

```
Approved PR → Merge → Close Issue → Delete Branch
```

## 🔧 分支管理策略

### 分支命名规范

```
agent/{agent_type}/{issue_id}

Examples:
- agent/code/123
- agent/fix/124
- agent/test/125
```

### 冲突避免机制

1. **原子性任务** - 每个Issue对应独立的修改范围
2. **分支隔离** - 每个Agent在独立分支工作
3. **依赖顺序** - 依赖任务串行执行
4. **独立文件** - 任务设计时避免文件冲突

### 最大并行度控制

```yaml
branch_strategy:
  max_parallel_agents: 5  # 最多5个Agent同时工作
  auto_cleanup: true       # 合并后自动删除分支
```

## 📁 项目结构

```
.
├── src/python_project/
│   ├── agents/                 # Agent实现
│   │   ├── base.py
│   │   ├── requirements_collector.py
│   │   ├── task_analyzer.py
│   │   └── pr_reviewer.py
│   ├── core/                   # 核心模块
│   │   ├── config.py
│   │   ├── github_client.py
│   │   └── claude_executor.py
│   ├── workflows/              # 工作流
│   │   └── orchestrator.py
│   └── main.py                 # 入口
├── docs/
│   ├── requirements/           # 需求文档
│   ├── issues/                 # Issue文档
│   └── workflow_runs/          # 运行记录
├── config/
│   └── config.yaml            # 配置文件
├── tests/                      # 测试
├── pyproject.toml
└── README.md
```

## 🧪 测试

```bash
# 运行所有测试
poetry run pytest

# 运行测试并生成覆盖率报告
poetry run pytest --cov=src/python_project

# 类型检查
poetry run mypy src
```

## 🛠️ 开发工具

```bash
# 代码格式化
poetry run black src tests

# Linter检查
poetry run ruff check src tests

# 类型检查
poetry run mypy src
```

## 📊 监控和调试

### 查看工作流状态

```bash
# 查看运行记录
cat docs/workflow_runs/run-YYYYMMDD-HHMMSS-*.json

# 查看任务分解
cat docs/tasks/task_breakdown.yaml
```

### 日志

每个Agent都会输出详细日志：

```
[agent-001] Starting requirements collection
[agent-001] Collected 5 requirements
[agent-001] Generated requirements.md
```

## 🔐 安全考虑

- GitHub Token和API Key通过环境变量管理
- 自动审核检查安全漏洞
- 分支保护规则
- PR审核机制

## 🚧 路线图

- [ ] Web UI界面
- [ ] 实时进度追踪
- [ ] 更多Agent类型
- [ ] 集成CI/CD
- [ ] 机器学习优化
- [ ] 多仓库支持

## 📝 License

MIT

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**: 这是一个自动化系统，建议在测试仓库中先进行充分测试后再用于生产环境。
