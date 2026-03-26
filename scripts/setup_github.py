#!/usr/bin/env python3
"""
Setup GitHub repository.
Creates a new repository and pushes the initial code.
"""

import os
import subprocess
import sys
from pathlib import Path

# Load environment variables
env_file = Path(".env.local")
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

import requests


def create_github_repo():
    """Create GitHub repository via API."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("[ERROR] GITHUB_TOKEN not found in .env.local")
        return False

    # Get username from token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    user_resp = requests.get("https://api.github.com/user", headers=headers)
    if user_resp.status_code != 200:
        print(f"[ERROR] Failed to get user info: {user_resp.json()}")
        return False

    username = user_resp.json()["login"]
    print(f"[OK] Authenticated as: {username}")

    # Check if repo exists
    repo_name = "AutoWorkOnGit"
    repo_resp = requests.get(
        f"https://api.github.com/repos/{username}/{repo_name}", headers=headers
    )

    if repo_resp.status_code == 200:
        print(f"[OK] Repository already exists: {username}/{repo_name}")
        return True

    # Create new repository
    print(f"[INFO] Creating repository: {username}/{repo_name}")
    create_resp = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json={
            "name": repo_name,
            "description": "Autonomous workflow system with Claude Code and multi-agent collaboration",
            "private": False,
            "has_issues": True,
            "has_projects": False,
            "has_wiki": False,
            "auto_init": False,
        },
    )

    if create_resp.status_code == 201:
        print(f"[OK] Repository created: {create_resp.json()['html_url']}")
        return True
    else:
        print(f"[ERROR] Failed to create repo: {create_resp.json()}")
        return False


def init_git_and_push():
    """Initialize git and push to GitHub."""
    print("\n[INFO] Initializing git repository...")

    commands = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit: Autonomous workflow system"],
        [
            "git",
            "remote",
            "add",
            "origin",
            f"https://github.com/benjonc/AutoWorkOnGit.git",
        ],
        ["git", "branch", "-M", "main"],
        ["git", "push", "-u", "origin", "main"],
    ]

    for cmd in commands:
        print(f"[RUN] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Command failed: {result.stderr}")
            # If it's the remote add command that failed, try to continue
            if "remote add" in " ".join(cmd):
                print("[INFO] Remote might already exist, trying to continue...")
                continue
            return False

    print("\n[SUCCESS] Repository initialized and pushed to GitHub!")
    print("[INFO] Repository URL: https://github.com/benjonc/AutoWorkOnGit")
    return True


def main():
    print("=" * 60)
    print("GitHub Repository Setup")
    print("=" * 60)

    # Step 1: Create GitHub repo
    if not create_github_repo():
        print("\n[FAILED] Could not create GitHub repository")
        return 1

    # Step 2: Initialize git and push
    if not init_git_and_push():
        print("\n[FAILED] Could not push to GitHub")
        print("[INFO] You may need to manually push:")
        print("  git remote add origin https://github.com/benjonc/AutoWorkOnGit.git")
        print("  git push -u origin main")
        return 1

    print("\n" + "=" * 60)
    print("[SUCCESS] Setup complete!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  poetry run python -m python_project")

    return 0


if __name__ == "__main__":
    sys.exit(main())
