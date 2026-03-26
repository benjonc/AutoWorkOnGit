"""Configuration management for the autonomous workflow system."""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class GitHubConfig(BaseModel):
    """GitHub configuration."""

    token: str = Field(..., description="GitHub personal access token")
    repo_owner: str = Field(..., description="Repository owner")
    repo_name: str = Field(..., description="Repository name")
    base_branch: str = Field(default="main", description="Base branch for PRs")


class ClaudeConfig(BaseModel):
    """Claude Code configuration."""

    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(default="claude-sonnet-4-6", description="Claude model to use")
    headless_timeout: int = Field(
        default=600, description="Timeout for headless execution (seconds)"
    )


class BranchStrategy(BaseModel):
    """Branch management strategy."""

    prefix_template: str = Field(
        default="agent/{agent_type}/{issue_id}", description="Branch naming template"
    )
    max_parallel_agents: int = Field(default=5, description="Maximum parallel agents")
    auto_cleanup: bool = Field(default=True, description="Auto-delete merged branches")


class Config(BaseModel):
    """Main configuration."""

    github: GitHubConfig
    claude: ClaudeConfig
    branch_strategy: BranchStrategy = BranchStrategy()
    workspace_root: Path = Field(default_factory=lambda: Path.cwd())
    docs_dir: Path = Field(default_factory=lambda: Path.cwd() / "docs")

    class Config:
        arbitrary_types_allowed = True


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        # Try to find project root (where pyproject.toml exists)
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                config_path = current / "config" / "config.yaml"
                break
            current = current.parent

        if config_path is None:
            # Fallback to current working directory
            config_path = Path.cwd() / "config" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Working directory: {Path.cwd()}\n"
            f"Please create config/config.yaml from config/config.yaml.example"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return Config(**data)
