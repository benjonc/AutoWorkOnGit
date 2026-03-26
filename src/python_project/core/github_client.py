"""GitHub API integration for issue and PR management."""

import logging
from typing import Optional

from github import Github, Issue, PullRequest, Repository
from github.GithubException import BadCredentialsException, UnknownObjectException

from python_project.core.config import GitHubConfig

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client wrapper with auto-create repository support."""

    def __init__(self, config: GitHubConfig, auto_create: bool = True):
        """
        Initialize GitHub client.

        Args:
            config: GitHub configuration
            auto_create: Automatically create repository if it doesn't exist
        """
        self.config = config
        self.client = Github(config.token)
        self.repo: Optional[Repository.Repository] = None

        # Verify authentication
        try:
            user = self.client.get_user()
            logger.info(f"Authenticated as GitHub user: {user.login}")
        except BadCredentialsException:
            raise ValueError(
                "GitHub authentication failed. Please check your GITHUB_TOKEN."
            )

        # Get or create repository
        self.repo = self._get_or_create_repository(auto_create=auto_create)

    def _get_or_create_repository(
        self, auto_create: bool = True
    ) -> Repository.Repository:
        """
        Get existing repository or create new one.

        Args:
            auto_create: Create repository if it doesn't exist

        Returns:
            Repository object

        Raises:
            ValueError: If repository doesn't exist and auto_create is False
        """
        repo_full_name = f"{self.config.repo_owner}/{self.config.repo_name}"

        # Try to get existing repository
        try:
            repo = self.client.get_repo(repo_full_name)
            logger.info(f"Repository found: {repo.full_name}")
            logger.info(f"  URL: {repo.html_url}")
            logger.info(f"  Stars: {repo.stargazers_count}, Forks: {repo.forks_count}")
            return repo
        except UnknownObjectException:
            # Repository doesn't exist
            if not auto_create:
                raise ValueError(
                    f"Repository not found: {repo_full_name}\n"
                    f"Set auto_create=True to create it automatically."
                )

            # Create repository
            logger.warning(f"Repository not found: {repo_full_name}")
            logger.info("Creating new repository...")

            return self._create_repository()

    def _create_repository(self) -> Repository.Repository:
        """
        Create a new GitHub repository.

        Returns:
            Created repository object
        """
        user = self.client.get_user()
        user_login = user.login

        # Check if we're creating for the authenticated user or an org
        is_user_repo = user_login == self.config.repo_owner

        if is_user_repo:
            # Create for authenticated user
            repo = user.create_repo(
                name=self.config.repo_name,
                description="Autonomous workflow system - managed by multi-agent AI",
                private=False,
                has_issues=True,
                has_projects=True,
                has_wiki=True,
                auto_init=False,
            )
        else:
            # Create for organization
            try:
                org = self.client.get_organization(self.config.repo_owner)
                repo = org.create_repo(
                    name=self.config.repo_name,
                    description="Autonomous workflow system - managed by multi-agent AI",
                    private=False,
                    has_issues=True,
                    has_projects=True,
                    has_wiki=True,
                    auto_init=False,
                )
            except UnknownObjectException:
                raise ValueError(
                    f"Organization not found: {self.config.repo_owner}\n"
                    f"Make sure you have access to this organization."
                )

        logger.info(f"Repository created: {repo.full_name}")
        logger.info(f"  URL: {repo.html_url}")

        # Create default branch if needed
        self._ensure_default_branch(repo)

        return repo

    def _ensure_default_branch(self, repo: Repository.Repository) -> None:
        """Ensure the default branch exists (create README if repo is empty)."""
        try:
            # Try to get the default branch
            default_branch = repo.default_branch
            logger.info(f"Default branch: {default_branch}")
        except Exception:
            # Repository is empty, create README
            logger.info("Repository is empty, creating initial commit...")
            try:
                repo.create_file(
                    path="README.md",
                    message="Initial commit",
                    content=f"# {repo.name}\n\n{repo.description or 'Repository for autonomous workflow system'}\n",
                    branch="main",
                )
                logger.info("Created README.md with initial commit")
            except Exception as e:
                logger.warning(f"Could not create initial commit: {e}")
                logger.info("You may need to initialize the repository manually")

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
