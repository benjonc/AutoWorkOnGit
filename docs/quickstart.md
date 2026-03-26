# 快速开始指南

本指南帮助你快速运行自动化工作流系统。

## 📋 前置检查

```bash
# 检查Python版本 (需要3.11+)
python --version

# 检查Poetry版本 (需要2.0+)
poetry --version

# 检查Git
git --version
```

## 🚀 5分钟快速启动

### 1. 安装依赖

```bash
# 安装所有依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 2. 配置环境变量

```bash
# 复制模板
cp .env.example .env.local

# 编辑.env.local，填入你的密钥
# 必填项:
# - GITHUB_TOKEN (GitHub Personal Access Token)
# - ANTHROPIC_API_KEY (Anthropic API Key)
```

#### 获取GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限:
   - ✅ `repo` (完整仓库访问)
   - ✅ `write:issues` (创建和管理Issues)
   - ✅ `write:pull_requests` (创建和管理PRs)
4. 复制生成的token到 `.env.local`

#### 获取Anthropic API Key

1. 访问 https://console.anthropic.com/
2. 进入 API Keys 页面
3. 创建新的API Key
4. 复制到 `.env.local`

### 3. 配置项目

编辑 `config/config.yaml`:

```yaml
github:
  repo_owner: "你的GitHub用户名"
  repo_name: "目标仓库名"
  base_branch: "main"  # 或 "master"
```

### 4. 运行系统

```bash
# 运行完整工作流
poetry run python -m python_project

# 或者激活环境后直接运行
poetry shell
python -m python_project
```

## 📝 第一次运行

系统会引导你完成以下步骤:

### Step 1: 需求收集

```
🤖 系统启动，开始需求收集...

请描述你的项目需求:
> 我想要一个用户认证系统，包括注册、登录和密码重置功能。

系统会继续询问:
- 目标用户是谁？
- 技术栈偏好？
- 特殊约束？

确认需求后生成: docs/requirements/requirements.md
```

### Step 2: 任务拆分

```
📊 分析需求，拆分任务...

✅ 生成 5 个任务:
  - TASK-001: 设计用户数据模型
  - TASK-002: 实现注册API
  - TASK-003: 实现登录API
  - TASK-004: 实现密码重置
  - TASK-005: 编写单元测试

依赖分析:
  Phase 1: [TASK-001]  (1个任务并行)
  Phase 2: [TASK-002, TASK-003, TASK-004]  (3个任务并行)
  Phase 3: [TASK-005]  (1个任务)
```

### Step 3: 创建Issues

```
📝 创建GitHub Issues...

✅ 创建Issue #123: 设计用户数据模型
✅ 创建Issue #124: 实现注册API
✅ 创建Issue #125: 实现登录API
✅ 创建Issue #126: 实现密码重置
✅ 创建Issue #127: 编写单元测试

保存到: docs/issues/
```

### Step 4: 并行执行

```
🚀 启动并行执行 (最多5个Agent)...

[Agent-001] 开始处理 Issue #123
  → 创建分支: agent/code/123_user-model
  → 使用Claude Code实现功能
  → 提交代码
  → 创建PR #10

[Agent-002] 开始处理 Issue #124
  → 等待依赖 #123 完成...
```

### Step 5: PR审核

```
🔍 审核PR #10...

审核结果: ✅ 通过
  - 代码质量: ✅
  - 测试覆盖: ✅
  - 文档完整: ✅
  - 安全检查: ✅

添加评论到PR...
```

### Step 6: 合并

```
🔀 合并PR #10...

✅ PR已合并
✅ Issue #123已关闭
✅ 分支已删除
```

## 🎯 示例项目

### 示例1: Web API项目

```bash
# 需求描述
"创建一个RESTful API，包括用户管理、文章CRUD和评论功能"

# 系统会自动:
1. 创建 ~10-15 个任务
2. 识别依赖关系
3. 并行实现功能
4. 自动测试和审核
5. 合并代码
```

### 示例2: 微服务拆分

```bash
# 需求描述
"将单体应用拆分为用户服务、订单服务和支付服务"

# 系统会:
1. 分析现有代码
2. 设计服务边界
3. 逐步拆分功能
4. 保证测试通过
5. 更新文档
```

## 🔧 常用命令

### 查看运行状态

```bash
# 查看最新运行记录
cat docs/workflow_runs/run-*.json | tail -1

# 查看任务分解
cat docs/tasks/task_breakdown.yaml

# 查看需求文档
cat docs/requirements/requirements.md
```

### 手动控制

```python
# 在Python中手动运行
from python_project.core.config import load_config
from python_project.workflows.orchestrator import WorkflowOrchestrator

config = load_config()
orchestrator = WorkflowOrchestrator(config)

# 启动
await orchestrator.start("manual-run-001")

# 执行特定阶段
await orchestrator._collect_requirements()
await orchestrator._analyze_dependencies()
```

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
poetry run python -m python_project
```

## 🐛 故障排查

### 问题1: GitHub Token权限不足

```
错误: Permission denied (publickey)
```

**解决**: 确保Token有 `repo` 权限

### 问题2: Claude API调用失败

```
错误: Invalid API key
```

**解决**: 检查 `.env.local` 中的 `ANTHROPIC_API_KEY`

### 问题3: 分支冲突

```
错误: Branch conflict detected
```

**解决**: 系统会自动创建修复任务，等待自动处理

### 问题4: 任务超时

```
错误: Execution exceeded 600 seconds
```

**解决**: 在 `config.yaml` 中增加 `headless_timeout`

## 📚 下一步

- 📖 阅读 [架构文档](./architecture.md) 了解系统设计
- 🔧 查看 [配置指南](./configuration.md) 自定义系统行为
- 🤝 阅读 [贡献指南](./contributing.md) 参与开发

## 💡 最佳实践

### 1. 需求描述要清晰

```bash
# ✅ 好的描述
"创建用户注册API，支持邮箱和密码，包含验证和密码加密"

# ❌ 模糊的描述
"做个注册功能"
```

### 2. 小步快跑

```bash
# ✅ 分阶段执行
第一次: "实现核心功能"
第二次: "添加测试"
第三次: "优化性能"

# ❌ 一次性完成所有
"实现完整的生产级系统，包括功能、测试、文档、性能优化..."
```

### 3. 监控运行状态

```bash
# 定期检查运行日志
tail -f docs/workflow_runs/latest.log
```

### 4. 人工介入点

- 需求确认时
- 架构决策时
- PR最终审核
- 关键配置变更

---

**遇到问题?** 查看 [常见问题](./faq.md) 或提交Issue
