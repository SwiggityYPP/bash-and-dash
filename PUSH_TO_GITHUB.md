# 🚀 Push to GitHub - Step by Step Guide

## Step 1: Open Command Prompt/PowerShell
Open Command Prompt or PowerShell in your project folder (where Bashanddash.py is located)

## Step 2: Initialize Git (if not already done)
```bash
git init
```

## Step 3: Set Your Git Identity (if not already done)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 4: Add GitHub Remote
```bash
git remote add origin https://github.com/SwiggityYPP/bash-and-dash.git
```

## Step 5: Add All Files
```bash
git add .
```

## Step 6: Make Your First Commit
```bash
git commit -m "Initial commit with auto-update system"
```

## Step 7: Set Default Branch (if needed)
```bash
git branch -M main
```

## Step 8: Push to GitHub
```bash
git push -u origin main
```

## Step 9: Create Your First Release
```bash
release.bat patch
```

---

## 📋 Complete Command Sequence (Copy & Paste)

```bash
git init
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git remote add origin https://github.com/SwiggityYPP/bash-and-dash.git
git add .
git commit -m "Initial commit with auto-update system"
git branch -M main
git push -u origin main
```

## 🎉 After This Works:

1. **Check GitHub**: Go to https://github.com/SwiggityYPP/bash-and-dash to see your files
2. **Create First Release**: Run `release.bat patch` to trigger the automated build
3. **Monitor Build**: Check the "Actions" tab on GitHub to watch the build process
4. **Download & Test**: Once built, download the .exe from the "Releases" tab

## 🔧 Troubleshooting:

**If you get "repository not found"**:
- Make sure you created the repository on GitHub.com first
- Ensure the repository name is exactly "bash-and-dash"

**If you get "permission denied"**:
- You might need to authenticate with GitHub (use GitHub Desktop or set up SSH keys)

**If git command not found**:
- Install Git from https://git-scm.com/

---

**Ready?** Copy the command sequence above and paste it into your terminal! 🚀
