"""
Version bump validation script.

Validates that version changes in pyproject.toml are proper increments.
Can be used in CI, pre-commit hooks, or run manually.

Usage:
    python scripts/check_version_bump.py [--comparison-ref REF]

Arguments:
    --comparison-ref: Git ref to compare against (default: HEAD~1 for commits, origin/main for PRs)
"""

import argparse
import subprocess
import sys

from packaging import version


def run_git_command(cmd):
    """Run a git command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def extract_version_from_pyproject(content):
    """Extract version from pyproject.toml content."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("version = "):
            # Extract version between quotes
            start = line.find('"')
            end = line.rfind('"')
            if start != -1 and end != -1 and start < end:
                return line[start + 1 : end]
    return None


def get_current_version():
    """Get version from current pyproject.toml."""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        return extract_version_from_pyproject(content)
    except FileNotFoundError:
        print("❌ Error: pyproject.toml not found")
        return None


def get_comparison_version(ref):
    """Get version from pyproject.toml at a specific git ref."""
    # Try to get the file content from git
    cmd = f"git show {ref}:pyproject.toml"
    content = run_git_command(cmd)

    if content is None:
        return None

    return extract_version_from_pyproject(content)


def is_in_git_repo():
    """Check if we're in a git repository."""
    return run_git_command("git rev-parse --git-dir") is not None


def detect_context():
    """Detect if we're in a PR context or regular commit."""
    # Check if GITHUB_EVENT_NAME environment variable exists (GitHub Actions)
    import os

    github_event = os.environ.get("GITHUB_EVENT_NAME")

    if github_event == "pull_request":
        return "pr"
    elif github_event == "push":
        return "push"
    else:
        # Default to commit context for local usage
        return "commit"


def main():
    parser = argparse.ArgumentParser(description="Validate version bump in pyproject.toml")
    parser.add_argument(
        "--comparison-ref",
        help="Git reference to compare against (default: auto-detect based on context)",
    )
    parser.add_argument(
        "--allow-same",
        action="store_true",
        help="Allow same version (no change required)",
    )

    args = parser.parse_args()

    # Check if we're in a git repo
    if not is_in_git_repo():
        print("❌ Error: Not in a git repository")
        sys.exit(1)

    # Get current version
    current_version = get_current_version()
    if not current_version:
        print("❌ Error: Could not extract version from pyproject.toml")
        sys.exit(1)

    print(f"Current version: {current_version}")

    # Determine comparison reference
    if args.comparison_ref:
        comparison_ref = args.comparison_ref
    else:
        context = detect_context()
        if context == "pr":
            comparison_ref = "origin/main"
        else:
            comparison_ref = "HEAD~1"

    print(f"Comparing against: {comparison_ref}")

    # Get comparison version
    comparison_version = get_comparison_version(comparison_ref)

    if comparison_version is None:
        print("✅ No previous version found (likely initial release)")
        sys.exit(0)

    print(f"Comparison version: {comparison_version}")

    # Check if versions are the same
    if current_version == comparison_version:
        if args.allow_same:
            print("ℹ️  No version change (allowed)")
            sys.exit(0)
        else:
            print("ℹ️  No version change detected")
            sys.exit(0)

    # Compare versions
    try:
        current_parsed = version.parse(current_version)
        comparison_parsed = version.parse(comparison_version)

        if current_parsed > comparison_parsed:
            print(f"✅ Version properly bumped: {comparison_version} → {current_version}")

            # Show what type of bump this is
            if current_parsed.major > comparison_parsed.major:
                print("   📈 Major version bump")
            elif current_parsed.minor > comparison_parsed.minor:
                print("   📈 Minor version bump")
            elif current_parsed.micro > comparison_parsed.micro:
                print("   📈 Patch version bump")
            else:
                print("   📈 Pre-release/metadata bump")

            sys.exit(0)
        else:
            print(f"❌ Invalid version change: {comparison_version} → {current_version}")
            print("   Version must increase. Please update to a higher version.")
            print(f"   Current: {current_version}")
            print(f"   Expected: > {comparison_version}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error parsing versions: {e}")
        print(f"   Current: {current_version}")
        print(f"   Comparison: {comparison_version}")
        sys.exit(1)


if __name__ == "__main__":
    main()
