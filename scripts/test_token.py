#!/usr/bin/env python3
"""Quick test of GitHub token."""

import os
import sys
from pathlib import Path

# Try to load .env.local
env_file = Path(".env.local")
if env_file.exists():
    print(f"[INFO] Loading .env.local...")
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value
                if "TOKEN" in key or "KEY" in key:
                    print(f"  {key}={value[:15]}...")
                else:
                    print(f"  {key}={value}")

token = os.getenv("GITHUB_TOKEN")
if not token:
    print("\n[ERROR] GITHUB_TOKEN not found!")
    print("Please create .env.local with:")
    print("  GITHUB_TOKEN=ghp_your_token_here")
    sys.exit(1)

print(f"\n[INFO] Testing token: {token[:15]}...")

try:
    from github import Github
    client = Github(token)
    user = client.get_user()
    print(f"[OK] Authenticated as: {user.login}")

    # Try to access the repo
    try:
        repo = client.get_repo("benjonc/AutoWorkOnGit")
        print(f"[OK] Repository accessible: {repo.full_name}")
        print("\n[SUCCESS] Token is valid!")
    except Exception as e:
        print(f"[ERROR] Cannot access repository: {e}")

except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    sys.exit(1)
