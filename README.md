# Bash and Dash Game Log Analyzer

## 🎮 About

A powerful game log analyzer for counting bash attacks and calculating payouts with a modern Discord-inspired dark theme UI.

**Current Version: 1.0.4**

### ✨ Latest Features (v1.0.4)
- �️ **Enhanced Mouse Wheel Scrolling** - Now works when hovering over any part of the payment commands list
- 📏 **Larger Default Window** - Increased from 550x520 to 550x700 for better visibility
- 🎨 **Modern Discord-Inspired UI** - Clean dark theme with improved visual hierarchy
- ⚡ **Improved User Experience** - Better spacing, fonts, and visual elements
- 🔧 **Bug Fixes** - Top basher payout now correctly included in total calculations

### 🎯 Key Features
- **Automatic bash attack detection** from game log files
- **Smart payout calculations** for both per-bash and top basher bonuses
- **One-click copy functionality** with visual feedback (strikethrough)
- **Real-time updates** when changing payout values
- **Auto-update system** checks for new releases on startup
- **Scrollable payment commands** with mouse wheel support

### One-Time Setup

1. **Create GitHub Repository**
   ```bash
   # Create a new repository on GitHub named 'bash-and-dash'
   # Then clone it and add your files
   git clone https://github.com/YourUsername/bash-and-dash.git
   cd bash-and-dash
   ```

2. **Update the Update URL**
   - Edit `Bashanddash.py`
   - Replace `YourUsername` in the `UPDATE_CHECK_URL` with your actual GitHub username

3. **Initial Commit**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

### 🎯 Releasing New Versions (Super Easy!)

#### Option 1: Use the Batch Script (Windows)
```bash
# Patch version (1.0.0 -> 1.0.1)
release.bat patch

# Minor version (1.0.0 -> 1.1.0)  
release.bat minor

# Major version (1.0.0 -> 2.0.0)
release.bat major

# Specific version
release.bat 1.2.3
```

#### Option 2: Use Python Script Directly
```bash
python update_version.py patch
python update_version.py minor
python update_version.py major
python update_version.py 1.2.3
```

### ✨ What Happens Automatically

1. **Version Update**: Script updates version in `Bashanddash.py`
2. **Git Commit**: Commits the version change
3. **Git Tag**: Creates a version tag (e.g., `v1.0.1`)
4. **GitHub Actions Trigger**: Tag push triggers the build workflow
5. **Build Executable**: GitHub builds the `.exe` file using PyInstaller
6. **Create Release**: Automatically creates a GitHub release
7. **Upload Executable**: Attaches the `.exe` file to the release
8. **Auto-Update Ready**: Users get notified of the new version

### 🔄 User Experience

- **First Time**: Users download the `.exe` from GitHub releases
- **Updates**: App automatically detects new versions and offers one-click updates
- **No Manual Downloads**: Users never need to manually download again

### 📁 File Structure
```
bash-and-dash/
├── .github/workflows/build-and-release.yml  # GitHub Actions workflow
├── Bashanddash.py                           # Main application
├── Bash-and-Dash.spec                       # PyInstaller configuration
├── update_version.py                        # Version management script
├── release.bat                              # Windows release script
├── requirements-build.txt                   # Build dependencies
└── README.md                                # This file
```

### 🛠 Customization

#### Custom Build Options
Edit `Bash-and-Dash.spec` to:
- Add custom icon: `icon='your-icon.ico'`
- Include data files
- Exclude unnecessary modules
- Add version information

#### Custom Release Notes
Edit `.github/workflows/build-and-release.yml` to customize the release description.

#### Alternative Update Sources
You can use any JSON endpoint instead of GitHub releases by:
1. Creating a simple JSON file: `{"version": "1.0.1", "download_url": "...", "changelog": "..."}`
2. Hosting it anywhere (GitHub raw, your website, etc.)
3. Updating `UPDATE_CHECK_URL` in the code

### 🎉 Benefits

- **Zero Manual Work**: One command releases everything
- **Professional Distribution**: GitHub releases with proper versioning
- **Automatic Updates**: Users get seamless update experience
- **Version Control**: Full git history of all versions
- **Backup**: GitHub stores all versions permanently
- **Statistics**: GitHub provides download statistics

### 🚨 Important Notes

- **GitHub Repository**: Must be public for free GitHub Actions
- **First Release**: Run `release.bat patch` to create your first automated release
- **Testing**: Test the update system with a small version increment first

### 📞 Support

If you encounter issues:
1. Check GitHub Actions tab for build logs
2. Ensure your GitHub repository is correctly set up
3. Verify the `UPDATE_CHECK_URL` points to your repository

---

**That's it!** Your application now has professional-grade automatic updates and distribution. 🎉
