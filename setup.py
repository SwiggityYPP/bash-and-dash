#!/usr/bin/env python3
"""
Bash and Dash Setup Script
==========================

This script helps you set up the automated release system.
"""

import os
import subprocess
import sys
import json

def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_git():
    """Check if git is installed and configured"""
    print("🔍 Checking Git setup...")
    
    stdout, stderr, code = run_command("git --version", check=False)
    if code != 0:
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    print(f"✅ Git found: {stdout}")
    
    # Check if we're in a git repo
    stdout, stderr, code = run_command("git status", check=False)
    if code != 0:
        print("📁 Not in a Git repository. Run 'git init' to initialize.")
        return False
    
    print("✅ In a Git repository")
    
    # Check git config
    stdout, stderr, code = run_command("git config user.name", check=False)
    if not stdout:
        print("⚠️  Git user.name not set. Run: git config --global user.name 'Your Name'")
        return False
    
    stdout, stderr, code = run_command("git config user.email", check=False)
    if not stdout:
        print("⚠️  Git user.email not set. Run: git config --global user.email 'your@email.com'")
        return False
    
    print("✅ Git is properly configured")
    return True

def check_github_repo():
    """Check if we have a GitHub remote"""
    print("\n🔍 Checking GitHub repository...")
    
    stdout, stderr, code = run_command("git remote -v", check=False)
    if "github.com" not in stdout:
        print("❌ No GitHub remote found.")
        print("Please create a GitHub repository and add it as remote:")
        print("  git remote add origin https://github.com/YourUsername/bash-and-dash.git")
        return False, None
    
    # Extract GitHub repo info
    lines = stdout.split('\n')
    for line in lines:
        if 'origin' in line and 'github.com' in line and '(push)' in line:
            # Extract repo info from URL
            if 'github.com/' in line:
                repo_part = line.split('github.com/')[-1].split('.git')[0].strip()
                print(f"✅ GitHub repository found: {repo_part}")
                return True, repo_part
    
    return False, None

def update_code_with_repo(repo_name):
    """Update the code with the correct GitHub repository"""
    print(f"\n🔧 Updating code with repository: {repo_name}")
    
    # Read the current file
    with open('Bashanddash.py', 'r') as f:
        content = f.read()
    
    # Update the URL
    old_url = 'UPDATE_CHECK_URL = "https://api.github.com/repos/YourUsername/bash-and-dash/releases/latest"'
    new_url = f'UPDATE_CHECK_URL = "https://api.github.com/repos/{repo_name}/releases/latest"'
    
    if old_url in content:
        content = content.replace(old_url, new_url)
        
        with open('Bashanddash.py', 'w') as f:
            f.write(content)
        
        print("✅ Updated UPDATE_CHECK_URL in Bashanddash.py")
        return True
    else:
        print("⚠️  Could not find UPDATE_CHECK_URL to update")
        return False

def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'Bashanddash.py',
        '.github/workflows/build-and-release.yml',
        'update_version.py',
        'release.bat',
        'README.md'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            all_good = False
    
    return all_good

def main():
    print("🚀 Bash and Dash Setup Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('Bashanddash.py'):
        print("❌ Bashanddash.py not found. Please run this from the project directory.")
        sys.exit(1)
    
    # Check Git
    if not check_git():
        print("\n❌ Git setup incomplete. Please fix the issues above.")
        sys.exit(1)
    
    # Check GitHub repo
    has_github, repo_name = check_github_repo()
    if not has_github:
        print("\n❌ GitHub repository not set up. Please:")
        print("1. Create a repository on GitHub named 'bash-and-dash'")
        print("2. Add it as remote: git remote add origin https://github.com/YourUsername/bash-and-dash.git")
        print("3. Run this script again")
        sys.exit(1)
    
    # Update code with correct repo
    if repo_name:
        update_code_with_repo(repo_name)
    
    # Check files
    if not check_files():
        print("\n❌ Some required files are missing. Please ensure all automation files are present.")
        sys.exit(1)
    
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("\nNext steps:")
    print("1. Commit all files: git add . && git commit -m 'Initial setup'")
    print("2. Push to GitHub: git push -u origin main")
    print("3. Create your first release: release.bat patch")
    print("\nAfter that, your auto-update system will be fully operational! 🚀")

if __name__ == "__main__":
    main()
