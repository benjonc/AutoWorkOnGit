"""Main workflow orchestrator for autonomous task execution."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional

import aiofiles
from pydantic import BaseModel

from python_project.core.claude_executor import ClaudeCodeExecutor
from python_project.core.config import Config
from python_project.core.github_client import GitHubClient


class WorkflowState(str, Enum):
    """Workflow execution states."""

    COLLECTING_REQUIREMENTS = "collecting_requirements"
    ANALYZING_DEPENDENCIES = "analyzing_dependencies"
    CREATING_ISSUES = "creating_issues"
    EXECUTING_TASKS = "executing_tasks"
    REVIEWING_PRS = "reviewing_prs"
    FIXING_ISSUES = "fixing_issues"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueStatus(BaseModel):
    """Issue tracking status."""

    issue_number: int
    title: str
    status: str  # "pending", "in_progress", "completed", "failed"
    branch_name: Optional[str] = None
    pr_number: Optional[int] = None
    dependencies: list[int] = []
    agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkflowRun(BaseModel):
    """Workflow run tracking."""

    run_id: str
    state: WorkflowState
    requirements_doc: Optional[str] = None
    issues: dict[int, IssueStatus] = {}
    created_at: datetime
    updated_at: datetime


class WorkflowOrchestrator:
    """
    Main orchestrator for the autonomous workflow.

    Coordinates:
    - Requirement collection with user
    - Dependency analysis and task breakdown
    - GitHub issue management
    - Parallel task execution via Claude Code
    - PR creation and review
    - Automated fixes and merging
    """

    def __init__(self, config: Config):
        self.config = config
        self.github_client = GitHubClient(config.github)
        self.claude_executor = ClaudeCodeExecutor(config.claude, config.workspace_root)
        self.run: Optional[WorkflowRun] = None

    async def start(self, run_id: str) -> None:
        """Start a new workflow run."""
        self.run = WorkflowRun(
            run_id=run_id,
            state=WorkflowState.COLLECTING_REQUIREMENTS,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self._save_run_state()

    async def execute(self) -> None:
        """Execute the complete workflow."""
        if not self.run:
            raise RuntimeError("Workflow not started. Call start() first.")

        try:
            # Phase 1: Collect requirements (interactive)
            await self._collect_requirements()

            # Phase 2: Analyze dependencies
            await self._analyze_dependencies()

            # Phase 3: Create GitHub issues
            await self._create_issues()

            # Phase 4: Execute tasks (parallel)
            await self._execute_tasks()

            # Phase 5: Review PRs
            await self._review_prs()

            # Phase 6: Fix issues if any
            await self._fix_issues()

            # Phase 7: Merge PRs and close issues
            await self._merge_and_close()

            self.run.state = WorkflowState.COMPLETED
            await self._save_run_state()

        except Exception:
            self.run.state = WorkflowState.FAILED
            await self._save_run_state()
            raise

    # ==================== Phase Implementations ====================

    async def _collect_requirements(self) -> None:
        """Phase 1: Interactive requirement collection."""
        self.run.state = WorkflowState.COLLECTING_REQUIREMENTS
        await self._save_run_state()

        # This will be implemented by the RequirementsCollector agent
        # For now, placeholder
        pass

    async def _analyze_dependencies(self) -> None:
        """Phase 2: Analyze task dependencies."""
        self.run.state = WorkflowState.ANALYZING_DEPENDENCIES
        await self._save_run_state()

        # This will be implemented by the TaskAnalyzer agent
        pass

    async def _create_issues(self) -> None:
        """Phase 3: Create GitHub issues for tasks."""
        self.run.state = WorkflowState.CREATING_ISSUES
        await self._save_run_state()

        # Create issues based on analyzed tasks
        pass

    async def _execute_tasks(self) -> None:
        """Phase 4: Execute tasks in parallel based on dependencies."""
        self.run.state = WorkflowState.EXECUTING_TASKS
        await self._save_run_state()

        while True:
            # Get tasks that can be executed (dependencies satisfied)
            executable_tasks = self._get_executable_tasks()

            if not executable_tasks:
                # Check if all tasks are completed
                if self._all_tasks_completed():
                    break
                # Wait for in-progress tasks to complete
                await asyncio.sleep(10)
                continue

            # Launch parallel agents up to max_parallel_agents
            tasks_to_run = executable_tasks[: self.config.branch_strategy.max_parallel_agents]

            await asyncio.gather(
                *[self._execute_single_task(issue_num) for issue_num in tasks_to_run]
            )

    async def _execute_single_task(self, issue_number: int) -> None:
        """Execute a single task (issue) with Claude Code."""
        issue_status = self.run.issues[issue_number]

        # Create branch
        branch_name = self._generate_branch_name(issue_number, issue_status.title)
        await self.github_client.create_branch(branch_name)

        # Update status
        issue_status.branch_name = branch_name
        issue_status.status = "in_progress"
        issue_status.agent_id = f"agent-{issue_number}"
        await self._save_run_state()

        # Execute task with Claude Code
        result = await self.claude_executor.execute(
            task_description=issue_status.title,
            context={"issue_number": issue_number},
        )

        if result["status"] == "success":
            # Create PR
            pr = await self.github_client.create_pr(
                title=f"Resolve #{issue_number}: {issue_status.title}",
                body=f"Closes #{issue_number}\n\n{result.get('message', '')}",
                head_branch=branch_name,
                draft=False,
            )

            issue_status.pr_number = pr.number
            issue_status.status = "completed"
        else:
            issue_status.status = "failed"

        issue_status.updated_at = datetime.now()
        await self._save_run_state()

    async def _review_prs(self) -> None:
        """Phase 5: Review all completed PRs."""
        self.run.state = WorkflowState.REVIEWING_PRS
        await self._save_run_state()

        # This will be implemented by the PRReviewer agent
        pass

    async def _fix_issues(self) -> None:
        """Phase 6: Fix issues found during review."""
        self.run.state = WorkflowState.FIXING_ISSUES
        await self._save_run_state()

        # Create fix tasks for failed reviews
        pass

    async def _merge_and_close(self) -> None:
        """Phase 7: Merge approved PRs and close issues."""
        self.run.state = WorkflowState.MERGING
        await self._save_run_state()

        for issue_num, issue_status in self.run.issues.items():
            if issue_status.pr_number and issue_status.status == "completed":
                # Merge PR
                await self.github_client.merge_pr(
                    pr_number=issue_status.pr_number,
                    commit_message=f"Resolve #{issue_num}: {issue_status.title}",
                )

                # Close issue
                await self.github_client.close_issue(
                    issue_number=issue_num,
                    comment=f"Resolved in PR #{issue_status.pr_number}",
                )

                # Delete branch if auto_cleanup is enabled
                if self.config.branch_strategy.auto_cleanup and issue_status.branch_name:
                    await self.github_client.delete_branch(issue_status.branch_name)

    # ==================== Helper Methods ====================

    def _get_executable_tasks(self) -> list[int]:
        """Get tasks whose dependencies are all completed."""
        executable = []
        for issue_num, status in self.run.issues.items():
            if status.status != "pending":
                continue

            # Check if all dependencies are completed
            deps_completed = all(
                self.run.issues[dep].status == "completed" for dep in status.dependencies
            )

            if deps_completed:
                executable.append(issue_num)

        return executable

    def _all_tasks_completed(self) -> bool:
        """Check if all tasks are completed."""
        return all(status.status in ("completed", "failed") for status in self.run.issues.values())

    def _generate_branch_name(self, issue_number: int, title: str) -> str:
        """Generate branch name following strategy."""
        # Convert title to branch-friendly format
        slug = title.lower().replace(" ", "-").replace("/", "-")[:50]
        template = self.config.branch_strategy.prefix_template
        return template.format(
            agent_type="code",
            issue_id=issue_number,
            slug=slug,
        )

    async def _save_run_state(self) -> None:
        """Save workflow run state to disk."""
        if not self.run:
            return

        state_file = self.config.docs_dir / "workflow_runs" / f"{self.run.run_id}.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(state_file, "w", encoding="utf-8") as f:
            await f.write(self.run.model_dump_json(indent=2))
