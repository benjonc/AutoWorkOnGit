#!/usr/bin/env python3
"""
Test GitHub repository auto-create functionality.
"""

import os
import sys
from pathlib import Path

# Load .env.local
env_file = Path(__file__).parent.parent / ".env.local"
if env_file.exists():
    print("[INFO] Loading .env.local...")
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

# Import after setting environment
from python_project.core.config import load_config
from python_project.core.github_client import GitHubClient


def test_repo_auto_create():
    """Test repository auto-creation."""
    print("=" * 60)
    print("Testing Repository Auto-Create")
    print("=" * 60)

    # Load config
    config = load_config()

    print(f"\n[INFO] Configuration:")
    print(f"  Owner: {config.github.repo_owner}")
    print(f"  Repo: {config.github.repo_name}")
    print(f"  Token: {config.github.token[:15]}...")

    # Create client with auto_create=True
    print("\n[INFO] Initializing GitHub client (auto_create=True)...")
    try:
        client = GitHubClient(config.github, auto_create=True)
        print(f"\n[SUCCESS] Repository ready!")
        print(f"  Full Name: {client.repo.full_name}")
        print(f"  URL: {client.repo.html_url}")
        print(f"  Description: {client.repo.description}")
        print(f"  Private: {client.repo.private}")
        print(f"  Default Branch: {client.repo.default_branch}")
        print(f"  Stars: {client.repo.stargazers_count}")
        print(f"  Forks: {client.repo.forks_count}")
        return 0
    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_repo_auto_create())

