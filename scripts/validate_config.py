#!/usr/bin/env python3
"""
Configuration validation script.
Run this to verify your setup before starting the workflow.
"""

import os
import sys
from pathlib import Path


def check_environment_variables():
    """Check required environment variables."""
    print("1. Checking environment variables...")

    required = {
        "GITHUB_TOKEN": "GitHub Personal Access Token",
        "ANTHROPIC_API_KEY": "Anthropic API Key",
    }

    missing = []
    for var, description in required.items():
        value = os.getenv(var)
        if value:
            # Mask the value for security
            masked = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            print(f"   ✓ {var}: {masked}")
        else:
            print(f"   ✗ {var}: NOT SET ({description})")
            missing.append(var)

    return missing


def check_config_file():
    """Check config file exists and is valid."""
    print("\n2. Checking configuration file...")

    config_path = Path("config/config.yaml")
    if not config_path.exists():
        print(f"   ✗ Config file not found: {config_path}")
        print(f"   → Create it from: config/config.yaml.example")
        return False

    print(f"   ✓ Config file found: {config_path}")

    # Try to load and parse
    try:
        import yaml

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Check required fields
        required_fields = [
            ("github.repo_owner", "GitHub username/org"),
            ("github.repo_name", "GitHub repository name"),
        ]

        missing_fields = []
        for field, description in required_fields:
            parts = field.split(".")
            value = data
            for part in parts:
                value = value.get(part, {})

            if not value or value == "your-username" or value == "your-repo":
                print(f"   ✗ {field}: NOT CONFIGURED ({description})")
                missing_fields.append(field)
            else:
                print(f"   ✓ {field}: {value}")

        return len(missing_fields) == 0

    except Exception as e:
        print(f"   ✗ Failed to parse config: {e}")
        return False


def check_github_connection():
    """Test GitHub API connection."""
    print("\n3. Testing GitHub connection...")

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("   ✗ Cannot test: GITHUB_TOKEN not set")
        return False

    try:
        from github import Github

        client = Github(token)
        user = client.get_user()
        print(f"   ✓ Authenticated as: {user.login}")

        # Try to access repo from config
        try:
            import yaml

            with open("config/config.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            repo_owner = data.get("github", {}).get("repo_owner")
            repo_name = data.get("github", {}).get("repo_name")

            if repo_owner and repo_name and repo_owner != "your-username":
                repo = client.get_repo(f"{repo_owner}/{repo_name}")
                print(f"   ✓ Repository accessible: {repo.full_name}")
            else:
                print("   ⚠ Repository not configured, skipping repo test")

        except Exception as e:
            print(f"   ✗ Repository access failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"   ✗ GitHub authentication failed: {e}")
        return False


def check_claude_api():
    """Test Claude API connection."""
    print("\n4. Testing Claude API...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("   ✗ Cannot test: ANTHROPIC_API_KEY not set")
        return False

    print("   ✓ API key is set (not testing actual API call)")
    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("Python Project - Configuration Validator")
    print("=" * 60)

    # Load .env.local if it exists
    env_file = Path(".env.local")
    if env_file.exists():
        print(f"\nLoading environment from: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

    # Run checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Configuration File", check_config_file),
        ("GitHub Connection", check_github_connection),
        ("Claude API", check_claude_api),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All checks passed! You're ready to run:")
        print("  poetry run python -m python_project")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  1. Create .env.local with your tokens")
        print("  2. Edit config/config.yaml with your repo details")
        print("  3. Re-run this validator: poetry run python scripts/validate_config.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
