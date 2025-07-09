@echo off
REM ============================================================================
REM Advanced Stealth Build Script for Bash and Dash Game Log Analyzer
REM ============================================================================
REM This script builds the executable with maximum stealth configurations
REM to minimize antivirus false positives.
REM 
REM Swiggity: Ultra-stealth executable generation
REM ============================================================================

echo Starting Advanced Stealth Build Process...
echo.

REM Clean previous builds
if exist "dist" (
    echo Cleaning previous build directory...
    rmdir /s /q "dist"
)

if exist "build" (
    echo Cleaning build cache...
    rmdir /s /q "build"
)

if exist "__pycache__" (
    echo Cleaning Python cache...
    rmdir /s /q "__pycache__"
)

if exist "Bashanddash.exe" (
    echo Removing old executable...
    del "Bashanddash.exe"
)

echo.
echo Verifying Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo.
echo Checking PyInstaller installation...
python -c "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)"
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller not found
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Building stealth executable...
echo Using spec file: Bashanddash-stealth.spec
echo Source file: Bashanddash-stealth.py

REM Build with advanced stealth options
python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --log-level=WARN ^
    --distpath="dist" ^
    --workpath="build" ^
    "Bashanddash-stealth.spec"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo Verifying build output...
if exist "dist\Bashanddash.exe" (
    echo SUCCESS: Executable created in dist directory
    
    REM Get file size
    for %%A in ("dist\Bashanddash.exe") do (
        echo File size: %%~zA bytes
    )
    
    REM Calculate hash
    echo Calculating file hash...
    certutil -hashfile "dist\Bashanddash.exe" SHA256 | findstr /v "hash"
    
    echo.
    echo Copying executable to root directory...
    copy "dist\Bashanddash.exe" "Bashanddash.exe"
    
    echo.
    echo Build completed successfully!
    echo.
    echo Files created:
    echo - dist\Bashanddash.exe (main output)
    echo - Bashanddash.exe (root copy)
    echo.
    echo Build timestamp: %date% %time%
    
) else (
    echo ERROR: Executable not found in expected location
    echo Build may have failed silently.
    pause
    exit /b 1
)

echo.
echo Advanced Stealth Build Process Complete!
echo.
echo SECURITY FEATURES ENABLED:
echo - Aggressive module exclusions
echo - Custom temporary directory naming
echo - Enhanced Windows manifest
echo - Stripped debug symbols
echo - Disabled UPX compression
echo - Filtered suspicious binaries
echo - Alternative network implementation
echo - Reduced subprocess usage
echo.
echo The executable should now have better antivirus compatibility.
echo Test with VirusTotal or your preferred scanning service.
echo.
pause
