# API 参考文档

本文档提供系统所有模块和类的详细API参考。

## 📚 核心模块 (Core)

### `python_project.core.config`

配置管理模块。

#### `Config`

主配置类。

```python
from python_project.core.config import Config

config = Config(
    github=GitHubConfig(
        token="ghp_xxx",
        repo_owner="username",
        repo_name="repo",
    ),
    claude=ClaudeConfig(
        api_key="sk-ant-xxx",
        model="claude-sonnet-4-6",
    ),
)
```

**属性**:

| 属性 | 类型 | 描述 |
|------|------|------|
| `github` | `GitHubConfig` | GitHub配置 |
| `claude` | `ClaudeConfig` | Claude配置 |
| `branch_strategy` | `BranchStrategy` | 分支策略 |
| `workspace_root` | `Path` | 工作空间根目录 |
| `docs_dir` | `Path` | 文档目录 |

#### `load_config()`

加载配置文件。

```python
from python_project.core.config import load_config

config = load_config()  # 从 config/config.yaml 加载
config = load_config(Path("custom/config.yaml"))
```

**参数**:
- `config_path` (Optional[Path]): 配置文件路径

**返回**: `Config`

**异常**:
- `FileNotFoundError`: 配置文件不存在
- `ValidationError`: 配置验证失败

---

### `python_project.core.github_client`

GitHub API客户端。

#### `GitHubClient`

GitHub API客户端封装。

```python
from python_project.core.github_client import GitHubClient

client = GitHubClient(config.github)

# 创建Issue
issue = await client.create_issue(
    title="Bug fix",
    body="Description",
    labels=["bug"],
)

# 创建PR
pr = await client.create_pr(
    title="Feature",
    body="Description",
    head_branch="feature/branch",
)

# 合并PR
await client.merge_pr(pr_number=10)
```

**方法**:

##### `create_issue()`

```python
async def create_issue(
    self,
    title: str,
    body: str,
    labels: Optional[list[str]] = None,
    assignees: Optional[list[str]] = None,
) -> Issue
```

创建GitHub Issue。

**参数**:
- `title`: Issue标题
- `body`: Issue内容
- `labels`: 标签列表
- `assignees`: 负责人列表

**返回**: `Issue`

##### `update_issue()`

```python
async def update_issue(
    self,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    labels: Optional[list[str]] = None,
    state: Optional[str] = None,
) -> Issue
```

更新Issue。

**参数**:
- `issue_number`: Issue编号
- `title`: 新标题
- `body`: 新内容
- `labels`: 新标签
- `state`: 新状态 ("open" 或 "closed")

**返回**: `Issue`

##### `create_pr()`

```python
async def create_pr(
    self,
    title: str,
    body: str,
    head_branch: str,
    base_branch: Optional[str] = None,
    draft: bool = False,
) -> PullRequest
```

创建Pull Request。

**参数**:
- `title`: PR标题
- `body`: PR内容
- `head_branch`: 源分支
- `base_branch`: 目标分支 (默认使用配置中的base_branch)
- `draft`: 是否为草稿

**返回**: `PullRequest`

##### `merge_pr()`

```python
async def merge_pr(
    self,
    pr_number: int,
    commit_message: Optional[str] = None,
    merge_method: str = "squash",
) -> bool
```

合并PR。

**参数**:
- `pr_number`: PR编号
- `commit_message`: 提交信息
- `merge_method`: 合并方法 ("merge", "squash", "rebase")

**返回**: `bool` (是否成功)

##### `create_branch()`

```python
async def create_branch(
    self,
    branch_name: str,
    base_branch: Optional[str] = None,
) -> None
```

创建分支。

**参数**:
- `branch_name`: 新分支名称
- `base_branch`: 基础分支

---

### `python_project.core.claude_executor`

Claude Code执行器。

#### `ClaudeCodeExecutor`

```python
from python_project.core.claude_executor import ClaudeCodeExecutor

executor = ClaudeCodeExecutor(config.claude, workspace_root)

# 执行任务
result = await executor.execute(
    task_description="Implement user login",
    context={
        "files_to_modify": ["src/auth/login.py"],
        "constraints": ["Use JWT tokens"],
    },
)
```

**方法**:

##### `execute()`

```python
async def execute(
    self,
    task_description: str,
    context: Optional[dict] = None,
    timeout: Optional[int] = None,
) -> dict
```

使用Claude Code执行任务。

**参数**:
- `task_description`: 任务描述
- `context`: 额外上下文
- `timeout`: 超时时间(秒)

**返回**:
```python
{
    "status": "success" | "error" | "timeout",
    "changes": [...],  # 修改的文件列表
    "commits": [...],  # 提交列表
    "message": "...",  # 执行消息
    "error": "...",    # 错误信息 (如果有)
}
```

---

## 🤖 Agent模块

### `python_project.agents.base`

Agent基类。

#### `BaseAgent`

所有Agent的基类。

```python
from python_project.agents.base import BaseAgent, AgentResult

class MyAgent(BaseAgent):
    async def execute(self, task: Any) -> AgentResult:
        # 实现具体逻辑
        return AgentResult(
            success=True,
            message="Task completed",
            data={"result": "..."},
        )
```

**方法**:

##### `execute()`

```python
@abstractmethod
async def execute(self, task: Any) -> AgentResult
```

执行Agent任务 (子类必须实现)。

##### `log()`

```python
def log(self, message: str) -> None
```

记录日志。

**参数**:
- `message`: 日志消息

#### `AgentResult`

执行结果。

```python
result = AgentResult(
    success=True,
    message="Completed",
    data={"key": "value"},
)
```

**属性**:
- `success` (bool): 是否成功
- `message` (str): 结果消息
- `data` (Optional[dict]): 额外数据

---

### `python_project.agents.requirements_collector`

需求收集Agent。

#### `RequirementsCollectorAgent`

```python
from python_project.agents.requirements_collector import RequirementsCollectorAgent

agent = RequirementsCollectorAgent(
    agent_id="req-collector-001",
    config=config,
)

result = await agent.execute(
    initial_request="Create a blog API"
)

print(result.data["document_path"])  # requirements.md路径
```

---

### `python_project.agents.task_analyzer`

任务分析Agent。

#### `TaskAnalyzerAgent`

```python
from python_project.agents.task_analyzer import TaskAnalyzerAgent

agent = TaskAnalyzerAgent(
    agent_id="task-analyzer-001",
    config=config,
)

result = await agent.execute(requirements_doc)

print(f"Generated {result.data['task_count']} tasks")
print(f"Max parallel: {result.data['max_parallel']}")
```

---

### `python_project.agents.pr_reviewer`

PR审核Agent。

#### `PRReviewAgent`

```python
from python_project.agents.pr_reviewer import PRReviewAgent

agent = PRReviewAgent(
    agent_id="pr-reviewer-001",
    config=config,
)

result = await agent.execute(
    pr_number=10,
    github_client=github_client,
)

if result.data["approved"]:
    print("✅ PR approved")
else:
    print(f"❌ {result.data['problems_count']} issues found")
```

---

## 🔄 工作流模块

### `python_project.workflows.orchestrator`

工作流编排器。

#### `WorkflowOrchestrator`

主工作流编排器。

```python
from python_project.workflows.orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(config)

# 启动工作流
await orchestrator.start("run-001")

# 执行完整流程
await orchestrator.execute()
```

**方法**:

##### `start()`

```python
async def start(self, run_id: str) -> None
```

启动工作流。

**参数**:
- `run_id`: 运行ID

##### `execute()`

```python
async def execute(self) -> None
```

执行完整工作流。

**异常**:
- `RuntimeError`: 如果未调用 `start()`

#### `WorkflowRun`

工作流运行状态。

```python
run = WorkflowRun(
    run_id="run-001",
    state=WorkflowState.COLLECTING_REQUIREMENTS,
    created_at=datetime.now(),
    updated_at=datetime.now(),
)
```

**属性**:
- `run_id` (str): 运行ID
- `state` (WorkflowState): 当前状态
- `requirements_doc` (Optional[str]): 需求文档路径
- `issues` (dict[int, IssueStatus]): Issue状态映射
- `created_at` (datetime): 创建时间
- `updated_at` (datetime): 更新时间

#### `IssueStatus`

Issue状态。

```python
status = IssueStatus(
    issue_number=123,
    title="Implement feature",
    status="pending",
    dependencies=[120, 121],
    created_at=datetime.now(),
    updated_at=datetime.now(),
)
```

**属性**:
- `issue_number` (int): Issue编号
- `title` (str): Issue标题
- `status` (str): 状态 ("pending", "in_progress", "completed", "failed")
- `branch_name` (Optional[str]): 分支名称
- `pr_number` (Optional[int]): PR编号
- `dependencies` (list[int]): 依赖的Issue编号
- `agent_id` (Optional[str]): 执行Agent ID
- `created_at` (datetime): 创建时间
- `updated_at` (datetime): 更新时间

---

## 🔧 工具模块

### `python_project.utils.logging`

日志工具。

#### `setup_logging()`

```python
from python_project.utils.logging import setup_logging

# 配置日志
setup_logging(level="INFO", log_file="logs/app.log")
```

**参数**:
- `level`: 日志级别
- `log_file`: 日志文件路径 (可选)

---

### `python_project.utils.retry`

重试工具。

#### `retry_with_backoff()`

```python
from python_project.utils.retry import retry_with_backoff

@retry_with_backoff(max_attempts=3, initial_delay=1)
async def unstable_operation():
    # 可能失败的操作
    pass
```

**参数**:
- `max_attempts`: 最大重试次数
- `initial_delay`: 初始延迟(秒)
- `backoff_factor`: 退避因子

---

## 📊 数据模型

### `WorkflowState`

工作流状态枚举。

```python
from python_project.workflows.orchestrator import WorkflowState

state = WorkflowState.EXECUTING_TASKS
```

**值**:
- `COLLECTING_REQUIREMENTS`: 收集需求中
- `ANALYZING_DEPENDENCIES`: 分析依赖中
- `CREATING_ISSUES`: 创建Issues中
- `EXECUTING_TASKS`: 执行任务中
- `REVIEWING_PRS`: 审核PR中
- `FIXING_ISSUES`: 修复Issues中
- `MERGING`: 合并中
- `COMPLETED`: 已完成
- `FAILED`: 已失败

---

## 🎯 完整示例

### 示例1: 手动执行单个任务

```python
import asyncio
from python_project.core.config import load_config
from python_project.core.github_client import GitHubClient
from python_project.core.claude_executor import ClaudeCodeExecutor

async def main():
    # 加载配置
    config = load_config()

    # 初始化客户端
    github_client = GitHubClient(config.github)
    executor = ClaudeCodeExecutor(config.claude, config.workspace_root)

    # 创建Issue
    issue = await github_client.create_issue(
        title="Add user authentication",
        body="Implement JWT-based authentication",
        labels=["enhancement"],
    )

    # 创建分支
    branch_name = f"agent/code/{issue.number}_auth"
    await github_client.create_branch(branch_name)

    # 执行任务
    result = await executor.execute(
        task_description=issue.title,
        context={"issue_number": issue.number},
    )

    if result["status"] == "success":
        # 创建PR
        pr = await github_client.create_pr(
            title=f"Resolve #{issue.number}: {issue.title}",
            body=f"Closes #{issue.number}",
            head_branch=branch_name,
        )

        print(f"✅ PR created: #{pr.number}")
    else:
        print(f"❌ Execution failed: {result['error']}")

asyncio.run(main())
```

### 示例2: 自定义Agent

```python
from python_project.agents.base import BaseAgent, AgentResult
from typing import Any

class DocumentationAgent(BaseAgent):
    """生成文档的Agent"""

    async def execute(self, code_files: list[str]) -> AgentResult:
        self.log(f"Generating docs for {len(code_files)} files")

        # 分析代码并生成文档
        docs = []
        for file in code_files:
            doc = await self._generate_doc(file)
            docs.append(doc)

        return AgentResult(
            success=True,
            message=f"Generated {len(docs)} documentation files",
            data={"docs": docs},
        )

    async def _generate_doc(self, file_path: str) -> str:
        # 使用Claude API生成文档
        # ... 实现细节
        pass

# 使用自定义Agent
agent = DocumentationAgent("doc-agent-001", config)
result = await agent.execute(["src/main.py", "src/utils.py"])
```

### 示例3: 批量操作

```python
import asyncio
from python_project.core.github_client import GitHubClient

async def batch_create_issues():
    github_client = GitHubClient(config.github)

    tasks = [
        {"title": "Task 1", "body": "Description 1"},
        {"title": "Task 2", "body": "Description 2"},
        {"title": "Task 3", "body": "Description 3"},
    ]

    # 并行创建所有Issues
    issues = await asyncio.gather(*[
        github_client.create_issue(**task)
        for task in tasks
    ])

    print(f"Created {len(issues)} issues")

asyncio.run(batch_create_issues())
```

---

## 🔍 错误处理

### 常见异常

#### `ConfigurationError`

配置错误。

```python
from python_project.core.exceptions import ConfigurationError

try:
    config = load_config()
except ConfigurationError as e:
    print(f"Invalid config: {e}")
```

#### `GitHubAPIError`

GitHub API错误。

```python
from python_project.core.exceptions import GitHubAPIError

try:
    issue = await github_client.create_issue(...)
except GitHubAPIError as e:
    print(f"GitHub API failed: {e}")
```

#### `ClaudeExecutionError`

Claude执行错误。

```python
from python_project.core.exceptions import ClaudeExecutionError

try:
    result = await executor.execute(...)
except ClaudeExecutionError as e:
    print(f"Execution failed: {e}")
```

---

## 📈 性能优化

### 缓存装饰器

```python
from python_project.utils.cache import cached

@cached(ttl=300)  # 缓存5分钟
async def expensive_operation():
    # 耗时操作
    pass
```

### 批量操作

```python
from python_project.utils.batch import batch_process

@batch_process(batch_size=10, delay=1)
async def process_items(items: list):
    # 批量处理
    pass
```

---

**提示**: 所有API都支持类型提示，建议使用IDE的自动完成功能
