#!/usr/bin/env python3
"""Version bumping script for GLAIP SDK.

This script provides convenient commands to bump version numbers:
- patch: 0.1.0 → 0.1.1 (bug fixes)
- minor: 0.1.0 → 0.2.0 (new features)
- major: 0.1.0 → 1.0.0 (breaking changes)

Usage:
    python scripts/bump_version.py patch    # Bump patch version
    python scripts/bump_version.py minor    # Bump minor version  
    python scripts/bump_version.py major    # Bump major version
    python scripts/bump_version.py --dry-run patch  # Preview changes
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_bump2version(version_type, dry_run=False):
    """Run bump2version with the specified version type."""
    cmd = ["bump2version"]
    
    if dry_run:
        cmd.append("--dry-run")
        cmd.append("--verbose")
    
    cmd.append(version_type)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running bump2version: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Bump GLAIP SDK version")
    parser.add_argument(
        "version_type",
        choices=["patch", "minor", "major"],
        help="Type of version bump to perform"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path(".bumpversion.cfg").exists():
        print("❌ Error: .bumpversion.cfg not found!")
        print("   Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    print(f"🚀 Bumping {args.version_type} version...")
    if args.dry_run:
        print("🔍 Dry run mode - no changes will be made")
    
    success = run_bump2version(args.version_type, args.dry_run)
    
    if success:
        if args.dry_run:
            print("✅ Dry run completed successfully")
        else:
            print(f"✅ Version bumped successfully!")
            print("💡 Don't forget to:")
            print("   - Push the changes: git push --follow-tags")
            print("   - Create a GitHub release for the new version")
    else:
        print("❌ Version bump failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
