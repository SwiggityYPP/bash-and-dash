# 🚀 Quick Setup Guide

## Step 1: Create GitHub Repository
1. Go to https://github.com
2. Click "New Repository" (green button)
3. Name it: `bash-and-dash`
4. Make it **Public** (required for free GitHub Actions)
5. Click "Create repository"

## Step 2: Connect Your Local Project
Open Command Prompt/PowerShell in your project folder and run:

```bash
# Initialize git (if not already done)
git init

# Add GitHub as remote (replace YourUsername with your actual GitHub username)
git remote add origin https://github.com/YourUsername/bash-and-dash.git

# Set your git identity (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Run Setup Script
```bash
python setup.py
```

This will:
- ✅ Check your Git setup
- ✅ Verify GitHub repository connection  
- ✅ Update the code with your repository URL
- ✅ Verify all automation files are present

## Step 4: Push Everything to GitHub
```bash
# Add all files
git add .

# Commit
git commit -m "Initial setup with auto-update system"

# Push to GitHub
git push -u origin main
```

## Step 5: Create Your First Release
```bash
# This will create version 1.0.1 and trigger the automated build
release.bat patch
```

## Step 6: Test the Auto-Update
1. Wait for GitHub Actions to finish building (check GitHub.com > your repo > Actions tab)
2. Download the generated `.exe` from Releases tab
3. Run it - it should show your app
4. Create another release with `release.bat patch`
5. The app should automatically detect and offer to update!

## 🎉 That's It!

Your app now has:
- ✅ Automatic building
- ✅ Automatic releasing  
- ✅ Automatic updates for users
- ✅ Professional distribution

## Future Releases
Just run: `release.bat patch` (or `minor`/`major`) and everything happens automatically!

---
**Need help?** Check the Actions tab on GitHub for build logs, or the README.md for more details.
