"""GitHub API integration for issue and PR management."""

from typing import Optional

from github import Github, Issue, PullRequest

from python_project.core.config import GitHubConfig


class GitHubClient:
    """GitHub API client wrapper."""

    def __init__(self, config: GitHubConfig):
        self.config = config
        self.client = Github(config.token)
        self.repo = self.client.get_repo(f"{config.repo_owner}/{config.repo_name}")

    # ==================== Issue Management ====================

    async def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[list[str]] = None,
        assignees: Optional[list[str]] = None,
    ) -> Issue.Issue:
        """Create a new GitHub issue."""
        issue = self.repo.create_issue(
            title=title,
            body=body,
            labels=labels or [],
            assignees=assignees or [],
        )
        return issue

    async def update_issue(
        self,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[list[str]] = None,
        state: Optional[str] = None,
    ) -> Issue.Issue:
        """Update an existing issue."""
        issue = self.repo.get_issue(issue_number)
        kwargs = {}
        if title:
            kwargs["title"] = title
        if body:
            kwargs["body"] = body
        if labels:
            kwargs["labels"] = labels
        if state:
            kwargs["state"] = state

        return issue.edit(**kwargs)

    async def get_issue(self, issue_number: int) -> Issue.Issue:
        """Get issue by number."""
        return self.repo.get_issue(issue_number)

    async def list_issues(
        self,
        state: str = "open",
        labels: Optional[list[str]] = None,
    ) -> list[Issue.Issue]:
        """List issues with filters."""
        kwargs = {"state": state}
        if labels:
            kwargs["labels"] = ",".join(labels)

        return list(self.repo.get_issues(**kwargs))

    async def close_issue(self, issue_number: int, comment: Optional[str] = None) -> Issue.Issue:
        """Close an issue with optional comment."""
        issue = self.repo.get_issue(issue_number)
        if comment:
            issue.create_comment(comment)
        return issue.edit(state="closed")

    # ==================== Pull Request Management ====================

    async def create_pr(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: Optional[str] = None,
        draft: bool = False,
    ) -> PullRequest.PullRequest:
        """Create a pull request."""
        pr = self.repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch or self.config.base_branch,
            draft=draft,
        )
        return pr

    async def get_pr(self, pr_number: int) -> PullRequest.PullRequest:
        """Get PR by number."""
        return self.repo.get_pull(pr_number)

    async def list_prs(
        self,
        state: str = "open",
        head: Optional[str] = None,
    ) -> list[PullRequest.PullRequest]:
        """List pull requests."""
        kwargs = {"state": state}
        if head:
            kwargs["head"] = head

        return list(self.repo.get_pulls(**kwargs))

    async def merge_pr(
        self,
        pr_number: int,
        commit_message: Optional[str] = None,
        merge_method: str = "squash",
    ) -> bool:
        """Merge a pull request."""
        pr = self.repo.get_pull(pr_number)
        if pr.mergeable:
            pr.merge(
                commit_message=commit_message or f"Merge PR #{pr_number}",
                merge_method=merge_method,
            )
            return True
        return False

    async def request_pr_review(
        self,
        pr_number: int,
        reviewers: list[str],
    ) -> None:
        """Request review on a PR."""
        pr = self.repo.get_pull(pr_number)
        pr.create_review_request(reviewers=reviewers)

    async def create_pr_comment(
        self,
        pr_number: int,
        body: str,
    ) -> None:
        """Add comment to a PR."""
        pr = self.repo.get_pull(pr_number)
        pr.create_issue_comment(body)

    # ==================== Branch Management ====================

    async def create_branch(
        self,
        branch_name: str,
        base_branch: Optional[str] = None,
    ) -> None:
        """Create a new branch."""
        base = self.repo.get_branch(base_branch or self.config.base_branch)
        self.repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base.commit.sha,
        )

    async def delete_branch(self, branch_name: str) -> None:
        """Delete a branch."""
        try:
            ref = self.repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
        except Exception:
            pass  # Branch may already be deleted after merge

    async def branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists."""
        try:
            self.repo.get_branch(branch_name)
            return True
        except Exception:
            return False
