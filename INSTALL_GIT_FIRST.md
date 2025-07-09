# 🚀 Complete GitHub Setup Guide

## ⚠️ First: Install Git

**Git is not installed on your system.** You need to install it first:

1. **Download Git**: Go to https://git-scm.com/download/win
2. **Install Git**: Run the installer with default settings
3. **Restart Command Prompt/PowerShell** after installation

## Alternative: Use GitHub Desktop (Easier)

If you prefer a visual interface:

1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Install and sign in** with your GitHub account
3. **Clone or create repository** through the interface
4. **Drag and drop your files** into the repository folder
5. **Commit and push** using the GUI

---

## Option A: Using Git Command Line (After Installing Git)

**Step 1: Open NEW Command Prompt/PowerShell** (after installing Git)

**Step 2: Navigate to your project folder**
```bash
cd "C:\Users\User"
```

**Step 3: Run setup commands**
```bash
git init
git config --global user.name "SwiggityYPP"
git config --global user.email "your.email@example.com"
git remote add origin https://github.com/SwiggityYPP/bash-and-dash.git
git add .
git commit -m "Initial commit with auto-update system"
git branch -M main
git push -u origin main
```

---

## Option B: Using GitHub Desktop (Recommended for Beginners)

1. **Create repository on GitHub.com**:
   - Go to https://github.com/SwiggityYPP/bash-and-dash
   - If it doesn't exist, create it by clicking "New Repository"

2. **Open GitHub Desktop**
3. **Clone the repository**:
   - File → Clone Repository
   - Enter: `SwiggityYPP/bash-and-dash`
   - Choose a location on your computer

4. **Copy your files**:
   - Copy all your project files to the cloned repository folder
   - GitHub Desktop will automatically detect the changes

5. **Commit and Push**:
   - Write a commit message: "Initial commit with auto-update system"
   - Click "Commit to main"
   - Click "Push origin"

---

## 🎯 What You Need to Do Right Now:

1. **Install Git** from https://git-scm.com/download/win
   - OR install **GitHub Desktop** from https://desktop.github.com/

2. **Create the repository** on GitHub.com:
   - Go to https://github.com/new
   - Repository name: `bash-and-dash`
   - Make it **Public**
   - Click "Create repository"

3. **Follow Option A or B** above to upload your files

## 🚀 After Upload Success:

Run this to create your first automated release:
```bash
release.bat patch
```

This will trigger the GitHub Actions to build your .exe file automatically!

---

**Need help?** The GitHub Desktop option is much easier if you're new to Git! 😊
