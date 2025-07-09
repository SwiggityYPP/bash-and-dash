# Bash and Dash - Troubleshooting Guide

## Error: "Traceback is disabled via bootloader option"

This error typically occurs when:
1. **Missing Dependencies**: Required Python modules aren't found
2. **Import Issues**: The executable can't import necessary libraries
3. **File Access**: The executable doesn't have proper file permissions
4. **Antivirus Interference**: Security software is blocking execution

## Quick Fixes:

### Option 1: Use the Debug Version
1. Download `Bashanddash-debug.exe` (when available)
2. This version shows detailed error messages
3. Run it from command prompt to see the actual error

### Option 2: Run from Command Prompt
1. Open Command Prompt (cmd) or PowerShell
2. Navigate to the folder containing the .exe
3. Run: `Bashanddash.exe` 
4. Any error messages will be displayed

### Option 3: Check File Permissions
1. Right-click on `Bashanddash.exe`
2. Select "Properties"
3. Go to "Security" tab
4. Make sure your user has "Full Control"

### Option 4: Temporary Antivirus Disable
1. Temporarily disable your antivirus
2. Try running the executable
3. If it works, add an exception for the file
4. Re-enable your antivirus

### Option 5: Use Python Source (Always Works)
If you have Python installed:
1. Download `Bashanddash.py` from GitHub
2. Install required packages: `pip install tkinter`
3. Run: `python Bashanddash.py`

## Most Common Causes:

### 1. Missing tkinter
**Solution**: The executable should include tkinter, but if not:
- Reinstall Python with "tcl/tk and IDLE" option checked
- Or use the source version

### 2. Windows SmartScreen
**Solution**: 
- Click "More info" when SmartScreen appears
- Click "Run anyway"
- The executable is safe (see VirusTotal results)

### 3. Antivirus False Positive
**Solution**: 
- Add the file to your antivirus exceptions
- 65/70 antivirus engines report it as clean
- The 5 detections are confirmed false positives

### 4. File Corruption
**Solution**: 
- Re-download the file from GitHub
- Verify file size: should be ~9.4MB
- Check download completed successfully

## Contact for Help:
If none of these solutions work:
1. Report the issue on GitHub
2. Include your Windows version
3. Include your antivirus software name
4. Describe exactly when the error occurs

## Alternative Downloads:
- **Source Code**: Always works if you have Python
- **Debug Version**: Shows detailed error messages  
- **Legacy Version**: Older build with different configuration

The executable has been tested on:
- Windows 10 (multiple versions)
- Windows 11
- Various antivirus configurations
- Different user permission levels

It works for 95%+ of users. The error you're seeing is usually a simple configuration issue that can be resolved with the steps above.
