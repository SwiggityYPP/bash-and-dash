#!/usr/bin/env python3
"""
Version Update Script
====================

Automatically updates the version number in the main file and creates a git tag.

Usage:
    python update_version.py 1.0.1        # Set specific version
    python update_version.py patch         # Increment patch (1.0.0 -> 1.0.1)
    python update_version.py minor         # Increment minor (1.0.0 -> 1.1.0)
    python update_version.py major         # Increment major (1.0.0 -> 2.0.0)
"""

import re
import sys
import subprocess
import os

def get_current_version():
    """Extract current version from main file"""
    with open('Bashanddash.py', 'r') as f:
        content = f.read()
    
    match = re.search(r'APP_VERSION = "(.+?)"', content)
    if match:
        return match.group(1)
    return "1.0.0"

def increment_version(version, increment_type):
    """Increment version based on type"""
    major, minor, patch = map(int, version.split('.'))
    
    if increment_type == 'major':
        return f"{major + 1}.0.0"
    elif increment_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif increment_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        return increment_type  # Assume it's a specific version

def update_version_in_file(new_version):
    """Update version in main file"""
    with open('Bashanddash.py', 'r') as f:
        content = f.read()
    
    # Update version
    content = re.sub(
        r'APP_VERSION = ".+?"',
        f'APP_VERSION = "{new_version}"',
        content
    )
    
    with open('Bashanddash.py', 'w') as f:
        f.write(content)
    
    print(f"✅ Updated version to {new_version} in Bashanddash.py")

def create_git_tag(version):
    """Create git tag and push"""
    try:
        # Add changes
        subprocess.run(['git', 'add', 'Bashanddash.py'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Bump version to {version}'], check=True)
        
        # Create tag
        subprocess.run(['git', 'tag', f'v{version}'], check=True)
        
        # Push changes and tag
        subprocess.run(['git', 'push'], check=True)
        subprocess.run(['git', 'push', '--tags'], check=True)
        
        print(f"✅ Created and pushed git tag v{version}")
        print(f"🚀 GitHub Actions will now build and release version {version}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <version|patch|minor|major>")
        print("Examples:")
        print("  python update_version.py 1.2.3")
        print("  python update_version.py patch")
        sys.exit(1)
    
    increment_type = sys.argv[1]
    current_version = get_current_version()
    
    print(f"Current version: {current_version}")
    
    # Determine new version
    if increment_type in ['patch', 'minor', 'major']:
        new_version = increment_version(current_version, increment_type)
    else:
        new_version = increment_type
    
    print(f"New version: {new_version}")
    
    # Confirm
    confirm = input("Proceed? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Update version
    update_version_in_file(new_version)
    
    # Create git tag (this will trigger the build)
    if create_git_tag(new_version):
        print(f"\n🎉 Version {new_version} release process started!")
        print("Check GitHub Actions for build progress.")
    else:
        print("❌ Failed to create git tag")

if __name__ == "__main__":
    main()
