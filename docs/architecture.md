# 系统架构设计

## 🏗️ 整体架构

```
┌────────────────────────────────────────────────────────────────────┐
│                         用户交互层                                   │
│                   (CLI / Web UI / API)                              │
└──────────────────────┬─────────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│                  Workflow Orchestrator                              │
│              (工作流编排器 - 核心协调器)                              │
│                                                                     │
│  • 状态管理 (WorkflowRun, IssueStatus)                              │
│  • 阶段调度 (7个阶段串行执行)                                         │
│  • Agent协调 (并行/串行任务分发)                                      │
│  • 异常处理 (重试,回滚,降级)                                          │
└────────┬──────────────┬──────────────┬──────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌──────────┐
    │ Agents  │    │  Core   │    │  Utils   │
    └─────────┘    └─────────┘    └──────────┘
         │              │              │
         │              │              │
         └──────────────┴──────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │     External Services       │
         ├─────────────────────────────┤
         │ • GitHub API                │
         │ • Claude Code CLI           │
         │ • Git Repository            │
         │ • File System               │
         └─────────────────────────────┘
```

## 🤖 Agent系统

### Agent类型与职责

| Agent | 输入 | 输出 | 职责 |
|-------|------|------|------|
| **RequirementsCollectorAgent** | 用户对话 | requirements.md | 收集、整理、结构化需求 |
| **TaskAnalyzerAgent** | requirements.md | task_breakdown.yaml | 拆分任务、分析依赖、生成执行计划 |
| **CodeExecutionAgent** | Issue描述 | 代码+PR | 使用Claude Code实现功能 |
| **PRReviewAgent** | PR内容 | 审核报告 | 自动化代码审核、质量检查 |

### Agent协作模式

```python
# 串行协作 (顺序依赖)
RequirementsCollectorAgent → TaskAnalyzerAgent → Issue创建

# 并行协作 (无依赖任务)
CodeExecutionAgent(issue_1) ┐
CodeExecutionAgent(issue_2) ├─ 并行执行
CodeExecutionAgent(issue_3) ┘
         ↓
    PRReviewAgent(pr_1) ┐
    PRReviewAgent(pr_2) ├─ 并行审核
    PRReviewAgent(pr_3) ┘
```

## 📊 工作流状态机

```
[COLLECTING_REQUIREMENTS]
         ↓
[ANALYZING_DEPENDENCIES]
         ↓
[CREATING_ISSUES]
         ↓
[EXECUTING_TASKS] ←──────┐
         ↓                │
[REVIEWING_PRS]           │
         ↓                │
    ┌─[通过]─→ [MERGING]  │
    │                     │
    └─[不通过]→ [FIXING_ISSUES] ─┘
                              │
                              ↓
                        [COMPLETED]
```

### 状态转换规则

| 当前状态 | 成功条件 | 下一状态 | 失败处理 |
|---------|---------|---------|---------|
| COLLECTING_REQUIREMENTS | requirements.md生成 | ANALYZING_DEPENDENCIES | 重新收集 |
| ANALYZING_DEPENDENCIES | task_breakdown.yaml生成 | CREATING_ISSUES | 重新分析 |
| CREATING_ISSUES | Issues创建成功 | EXECUTING_TASKS | 重试创建 |
| EXECUTING_TASKS | 所有任务完成 | REVIEWING_PRS | 标记失败任务 |
| REVIEWING_PRS | 所有PR审核完成 | MERGING 或 FIXING_ISSUES | 重新审核 |
| FIXING_ISSUES | 修复完成 | REVIEWING_PRS | 创建新修复任务 |
| MERGING | PR合并成功 | COMPLETED | 回滚或人工介入 |

## 🔄 并行执行策略

### 依赖图分析

```python
# 任务依赖图示例
tasks = {
    "TASK-001": [],                    # 无依赖
    "TASK-002": ["TASK-001"],          # 依赖TASK-001
    "TASK-003": ["TASK-001"],          # 依赖TASK-001
    "TASK-004": [],                    # 无依赖
    "TASK-005": ["TASK-004", "TASK-002"]  # 多重依赖
}

# 执行阶段
Phase 1: [TASK-001, TASK-004]  # 并行执行
Phase 2: [TASK-002, TASK-003]  # 并行执行
Phase 3: [TASK-005]            # 串行执行
```

### 并行度控制

```yaml
# config.yaml
branch_strategy:
  max_parallel_agents: 5  # 最多5个Agent同时工作
```

**控制策略**:
1. 每个阶段开始时，检查可用Agent槽位
2. 按优先级调度任务
3. 实时监控资源使用
4. 动态调整并行度

## 🌳 分支管理策略

### 分支命名规范

```
agent/{agent_type}/{issue_id}_{short_slug}

Examples:
- agent/code/123_user-auth
- agent/fix/124_api-bug
- agent/test/125_unit-tests
- agent/docs/126_readme-update
```

### 分支生命周期

```
1. 创建分支
   ↓
2. Agent工作 (commit, push)
   ↓
3. 创建PR (draft: false)
   ↓
4. 审核通过
   ↓
5. 合并到base branch
   ↓
6. 自动删除分支 (if auto_cleanup: true)
```

### 冲突避免机制

#### 1. 任务隔离原则

```python
# 任务设计时确保文件隔离
task_1 = {
    "files_to_modify": ["src/auth/user.py"],
    "files_created": ["src/auth/models.py"],
}

task_2 = {
    "files_to_modify": ["src/api/endpoints.py"],
    "files_created": ["src/api/schemas.py"],
}
# ✅ 无文件重叠，可并行执行
```

#### 2. 依赖串行化

```python
# 有文件冲突的任务建立依赖关系
task_1 = {
    "files_to_modify": ["src/models/user.py"],
}

task_2 = {
    "files_to_modify": ["src/models/user.py"],  # 冲突!
    "dependencies": ["TASK-001"],  # 串行执行
}
```

#### 3. 锁机制 (高级)

```python
# 文件锁 - 防止同时修改
file_locks = {
    "src/core/config.py": "agent-001",
    "src/database/db.py": "agent-002",
}

# Agent在修改文件前检查锁
async def modify_file(file_path: str):
    if file_path in file_locks:
        await wait_for_unlock(file_path)
    acquire_lock(file_path)
    # ... 修改文件 ...
    release_lock(file_path)
```

## 📝 Issue管理策略

### Issue模板

```markdown
# {Task Title}

## 📋 任务描述
{Detailed task description}

## ✅ 验收标准
- [ ] {Criterion 1}
- [ ] {Criterion 2}

## 📎 相关信息
- **需求来源**: FR-XXX
- **预估工时**: X hours
- **依赖任务**: #YYY

## 💡 技术提示
{Implementation hints for agent}
```

### Issue状态追踪

```python
class IssueStatus:
    issue_number: int
    status: str  # "pending" | "in_progress" | "completed" | "failed"
    branch_name: Optional[str]
    pr_number: Optional[int]
    dependencies: list[int]
    agent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Issue生命周期

```
[创建] → [pending]
            ↓ Agent领取
        [in_progress]
            ↓ 完成实现
        [PR创建]
            ↓ 审核通过
        [completed] → [关闭Issue]
            ↓ 审核失败
        [failed] → [创建修复Issue]
```

## 🔍 PR审核机制

### 审核检查项

```python
REVIEW_CRITERIA = [
    "code_quality",      # 代码质量
    "test_coverage",     # 测试覆盖率
    "documentation",     # 文档完整性
    "security",          # 安全漏洞
    "performance",       # 性能问题
    "architecture",      # 架构一致性
]
```

### 审核流程

```
1. 获取PR变更文件
   ↓
2. 逐文件检查 (使用Claude API)
   ↓
3. 生成审核报告
   ↓
4. 添加PR评论
   ↓
5. 决策:
   - 通过 → 添加 "approved" 标签
   - 不通过 → 创建修复Issue
```

### 修复Issue创建

```python
# 审核发现问题
problems = [
    {
        "severity": "error",
        "file": "src/auth/login.py",
        "message": "Missing input validation",
        "line": 42,
    }
]

# 自动创建修复Issue
github_client.create_issue(
    title=f"Fix PR #{pr_number} - Missing input validation",
    body=f"""
## PR Review Issue

**PR Number**: #{pr_number}
**File**: src/auth/login.py:42
**Severity**: error

### Problem
Missing input validation

### Suggested Fix
Add input validation using Pydantic model
""",
    labels=["automated-review", "fix-required"],
)
```

## 🛡️ 容错机制

### 重试策略

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def execute_task(issue_number: int):
    # 任务执行
    pass
```

### 失败处理

```python
# 任务失败处理
if result.status == "failed":
    # 1. 记录失败原因
    log_error(issue_number, result.error)

    # 2. 创建错误Issue
    create_error_issue(issue_number, result.error)

    # 3. 标记任务状态
    update_issue_status(issue_number, "failed")

    # 4. 通知人工介入
    notify_maintainers(issue_number, result.error)
```

### 回滚机制

```python
# PR合并后发现问题
async def rollback_pr(pr_number: int):
    # 1. Revert PR
    pr = github_client.get_pr(pr_number)
    pr.revert()

    # 2. 重新打开Issue
    issue_number = extract_issue_from_pr(pr)
    github_client.update_issue(issue_number, state="open")

    # 3. 创建新的修复任务
    create_fix_issue(issue_number, "Regression detected")
```

## 📈 性能优化

### 缓存策略

```python
# 缓存Claude API调用结果
@lru_cache(maxsize=100)
async def analyze_code(file_path: str, content_hash: str):
    # 分析代码结构
    pass

# 缓存GitHub API响应
@cached(ttl=300)  # 5分钟
async def get_issue_dependencies(issue_number: int):
    # 获取Issue依赖
    pass
```

### 批量操作

```python
# 批量创建Issues
async def create_issues_batch(tasks: list[Task]):
    issues = await asyncio.gather(*[
        github_client.create_issue(
            title=task.title,
            body=task.description,
        )
        for task in tasks
    ])
    return issues

# 批量合并PRs
async def merge_prs_batch(pr_numbers: list[int]):
    results = await asyncio.gather(*[
        github_client.merge_pr(pr_number)
        for pr_number in pr_numbers
    ])
    return results
```

## 🔐 安全考虑

### API密钥管理

```python
# 从环境变量读取
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# 永远不要硬编码
# ❌ BAD
token = "ghp_xxxxxxxxx"

# ✅ GOOD
token = os.environ.get("GITHUB_TOKEN")
```

### 分支保护

```yaml
# GitHub Branch Protection Rules
main:
  required_pull_request_reviews: true
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
```

### 权限控制

```python
# Agent权限分级
class AgentPermissions:
    READ_ONLY = ["requirements_collector", "task_analyzer"]
    READ_WRITE = ["code_executor"]
    ADMIN = ["pr_reviewer", "orchestrator"]

# 操作前权限检查
def check_permission(agent: Agent, operation: str):
    if operation not in agent.allowed_operations:
        raise PermissionError(f"Agent {agent.id} cannot perform {operation}")
```

## 📊 监控与可观测性

### 日志系统

```python
# 结构化日志
logger.info(
    "Task execution started",
    extra={
        "run_id": run_id,
        "issue_number": issue_number,
        "agent_id": agent_id,
    }
)

# 日志级别
DEBUG: 详细的执行细节
INFO:  关键操作和状态变更
WARN:  可恢复的异常
ERROR: 任务失败
```

### 指标收集

```python
# Prometheus指标
task_duration = Histogram(
    'task_duration_seconds',
    'Time spent executing tasks',
    ['agent_type', 'task_status']
)

parallel_agents = Gauge(
    'active_parallel_agents',
    'Number of agents currently running'
)

pr_review_pass_rate = Counter(
    'pr_review_pass_total',
    'Number of PRs that passed review'
)
```

### 追踪系统

```python
# OpenTelemetry追踪
with tracer.start_as_current_span("execute_task") as span:
    span.set_attribute("issue_number", issue_number)
    span.set_attribute("agent_id", agent_id)

    result = await execute_task(issue_number)

    span.set_attribute("status", result.status)
```

---

**下一步**: 查看 [API文档](./api.md) 了解详细的接口规范
