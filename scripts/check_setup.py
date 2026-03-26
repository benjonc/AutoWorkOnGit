#!/usr/bin/env python3
"""
Simple setup checker - verifies the basic configuration.
"""

import os
import sys
from pathlib import Path


def load_env_file():
    """Load .env.local if it exists."""
    env_file = Path(".env.local")
    if env_file.exists():
        print("[OK] Found .env.local")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
        return True
    else:
        print("[FAIL] .env.local not found")
        return False


def check_tokens():
    """Check if tokens are set."""
    print("\nChecking tokens...")

    github_token = os.getenv("GITHUB_TOKEN")
    if github_token and github_token != "ghp_your_token_here":
        print(f"✓ GITHUB_TOKEN is set ({github_token[:10]}...)")
    else:
        print("✗ GITHUB_TOKEN not set or using placeholder")
        print("  → Get it from: https://github.com/settings/tokens/new")
        print("  → Add to .env.local: GITHUB_TOKEN=ghp_xxxxx")
        return False

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "sk-ant-your_key_here":
        print(f"✓ ANTHROPIC_API_KEY is set ({api_key[:15]}...)")
    else:
        print("✗ ANTHROPIC_API_KEY not set or using placeholder")
        print("  → Get it from: https://console.anthropic.com/")
        print("  → Add to .env.local: ANTHROPIC_API_KEY=sk-ant-xxxxx")
        return False

    return True


def check_github_access():
    """Test GitHub API access."""
    print("\nTesting GitHub access...")

    try:
        from github import Github

        token = os.getenv("GITHUB_TOKEN")
        client = Github(token)
        user = client.get_user()
        print(f"✓ Authenticated as GitHub user: {user.login}")

        # Try to get repo from config
        try:
            import yaml

            with open("config/config.yaml", "r") as f:
                config = yaml.safe_load(f)

            owner = config.get("github", {}).get("repo_owner", "")
            repo = config.get("github", {}).get("repo_name", "")

            if owner == "your-username":
                print("⚠ repo_owner still using placeholder 'your-username'")
                print("  → Edit config/config.yaml and set your actual GitHub username")
                return False

            if repo == "your-repo":
                print("⚠ repo_name still using placeholder 'your-repo'")
                print("  → Edit config/config.yaml and set your actual repository name")
                return False

            # Try to access the repo
            full_repo = f"{owner}/{repo}"
            repo_obj = client.get_repo(full_repo)
            print(f"✓ Repository accessible: {repo_obj.full_name}")
            return True

        except FileNotFoundError:
            print("✗ config/config.yaml not found")
            return False
        except Exception as e:
            print(f"✗ Failed to access repository: {e}")
            return False

    except Exception as e:
        print(f"✗ GitHub authentication failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Quick Setup Checker")
    print("=" * 60)

    # Load env
    env_loaded = load_env_file()

    # Run checks
    tokens_ok = check_tokens()
    github_ok = check_github_access() if tokens_ok else False

    # Summary
    print("\n" + "=" * 60)
    if tokens_ok and github_ok:
        print("✓ All checks passed!")
        print("\nYou're ready to run:")
        print("  poetry run python -m python_project")
        return 0
    else:
        print("✗ Setup incomplete")
        print("\nNext steps:")
        if not env_loaded:
            print("  1. Create .env.local from .env.example")
        if not tokens_ok:
            print("  2. Add your tokens to .env.local")
        if not github_ok:
            print("  3. Update config/config.yaml with your repo details")
        print("\nFor detailed instructions, see SETUP_GUIDE.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
