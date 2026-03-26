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
    import os
    import re

    # Load .env.local first
    env_file = Path.cwd() / ".env.local"
    if not env_file.exists():
        # Try project root
        env_file = Path(__file__).resolve().parent.parent.parent.parent / ".env.local"

    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

    if config_path is None:
        # Try multiple locations
        possible_paths = [
            # From src directory (where __main__.py runs)
            Path(__file__).resolve().parent.parent.parent.parent / "config" / "config.yaml",
            # From project root
            Path.cwd() / "config" / "config.yaml",
            # From src parent
            Path.cwd().parent / "config" / "config.yaml",
        ]

        for path in possible_paths:
            if path.exists():
                config_path = path
                break

        if config_path is None:
            # Last resort: try to find by walking up
            current = Path(__file__).resolve().parent
            while current != current.parent:
                config_candidate = current / "config" / "config.yaml"
                if config_candidate.exists():
                    config_path = config_candidate
                    break
                current = current.parent

    if config_path is None or not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found.\n"
            f"Working directory: {Path.cwd()}\n"
            f"Please create config/config.yaml from config/config.yaml.example"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace environment variables ${VAR_NAME}
    def replace_env(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))

    content = re.sub(r"\$\{([^}]+)\}", replace_env, content)
    data = yaml.safe_load(content)

    return Config(**data)
