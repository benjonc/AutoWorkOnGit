"""PR review agent - automated code review using Claude."""

from typing import Any

from github import PullRequest

from python_project.agents.base import AgentResult, BaseAgent
from python_project.core.github_client import GitHubClient


class PRReviewAgent(BaseAgent):
    """
    Agent responsible for reviewing pull requests.

    Checks:
    - Code quality and style
    - Test coverage
    - Documentation
    - Security issues
    - Performance concerns
    - Architectural alignment
    """

    # Review checklist
    REVIEW_CRITERIA = [
        "code_quality",
        "test_coverage",
        "documentation",
        "security",
        "performance",
        "architecture",
    ]

    async def execute(self, pr_number: int, github_client: GitHubClient) -> AgentResult:
        """
        Execute automated PR review.

        Args:
            pr_number: Pull request number
            github_client: GitHub client for API calls

        Returns:
            AgentResult with review outcome and feedback
        """
        self.log(f"Reviewing PR #{pr_number}")

        # Fetch PR details
        pr = await github_client.get_pr(pr_number)

        # Get PR diff/files
        files = pr.get_files()

        # Conduct review
        review_result = await self._conduct_review(pr, files)

        # Post review as PR comment
        await self._post_review(pr, review_result)

        if not review_result["approved"]:
            # Create fix issues for problems found
            await self._create_fix_issues(
                pr_number=pr_number,
                problems=review_result["problems"],
                github_client=github_client,
            )

        status = "approved" if review_result["approved"] else "changes requested"
        return AgentResult(
            success=True,
            message=f"PR review completed - {status}",
            data={
                "pr_number": pr_number,
                "approved": review_result["approved"],
                "problems_count": len(review_result["problems"]),
                "review_summary": review_result["summary"],
            },
        )

    async def _conduct_review(
        self,
        pr: PullRequest.PullRequest,
        files: list[Any],
    ) -> dict:
        """
        Conduct comprehensive PR review.

        In real implementation, would use Claude API to analyze code.
        """
        problems = []
        approved = True

        # Check each file
        for file in files:
            # Simulated review logic
            if file.additions > 500:
                problems.append(
                    {
                        "severity": "warning",
                        "file": file.filename,
                        "message": "Large file change - consider breaking into smaller PRs",
                    }
                )

            # Check for test files
            if not any("test" in f.filename.lower() for f in files):
                problems.append(
                    {
                        "severity": "error",
                        "file": "general",
                        "message": "No test files found - tests are required",
                    }
                )
                approved = False

        # Check PR description
        if len(pr.body) < 20:
            problems.append(
                {
                    "severity": "warning",
                    "file": "general",
                    "message": "PR description is too brief",
                }
            )

        return {
            "approved": approved,
            "problems": problems,
            "summary": f"Found {len(problems)} issues in {len(files)} files",
        }

    async def _post_review(self, pr: PullRequest.PullRequest, review_result: dict) -> None:
        """Post review comment on PR."""
        # Format review comment
        if review_result["approved"]:
            comment = "## ✅ Automated Review: APPROVED\n\n"
        else:
            comment = "## ⚠️ Automated Review: CHANGES REQUESTED\n\n"

        comment += f"{review_result['summary']}\n\n"

        if review_result["problems"]:
            comment += "### Issues Found:\n\n"
            for problem in review_result["problems"]:
                emoji = "⚠️" if problem["severity"] == "warning" else "❌"
                comment += f"{emoji} **{problem['file']}**: {problem['message']}\n"

        pr.create_issue_comment(comment)

    async def _create_fix_issues(
        self,
        pr_number: int,
        problems: list[dict],
        github_client: GitHubClient,
    ) -> None:
        """Create fix issues for review problems."""
        for idx, problem in enumerate(problems, 1):
            if problem["severity"] == "error":
                await github_client.create_issue(
                    title=f"Fix PR #{pr_number} - Issue {idx}: {problem['message']}",
                    body=f"""
## PR Review Issue

**PR Number**: #{pr_number}
**File**: {problem['file']}
**Severity**: {problem['severity']}

### Problem
{problem['message']}

### Context
This issue was identified during automated PR review.

### Action Required
Please address this issue by making the necessary changes.
""",
                    labels=["automated-review", "fix-required"],
                )
