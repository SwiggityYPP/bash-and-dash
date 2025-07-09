@echo off
REM ============================================================================
REM Bash and Dash Game Log Analyzer - Secure Build Script
REM ============================================================================
REM
REM This script builds the executable with security-focused settings to
REM minimize antivirus false positives.
REM
REM Swiggity: Comprehensive build process with security optimizations
REM ============================================================================

echo ================================================
echo Bash and Dash Game Log Analyzer - Secure Build
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Check if PyInstaller is available
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo ✓ PyInstaller installed
) else (
    echo ✓ PyInstaller found
)
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
if exist "Bashanddash.exe" del "Bashanddash.exe"
echo ✓ Cleanup complete
echo.

REM Build with secure settings
echo Building executable with security optimizations...
echo This may take several minutes...
echo.

python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --log-level=WARN ^
    --distpath=dist ^
    --workpath=build ^
    Bashanddash-secure.spec

if errorlevel 1 (
    echo.
    echo ❌ Build FAILED
    echo Check the output above for errors.
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\Bashanddash.exe" (
    echo.
    echo ❌ Build completed but executable not found
    echo Expected location: dist\Bashanddash.exe
    pause
    exit /b 1
)

REM Copy executable to root directory
copy "dist\Bashanddash.exe" "Bashanddash.exe" >nul
if errorlevel 1 (
    echo.
    echo ❌ Failed to copy executable to root directory
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ BUILD SUCCESSFUL
echo ================================================
echo.
echo Executable created: Bashanddash.exe
echo Size: 
for %%i in (Bashanddash.exe) do echo %%~zi bytes
echo.
echo Security features enabled:
echo • No UPX compression (reduces AV flags)
echo • Proper Windows manifest
echo • Detailed version information
echo • Secure import filtering
echo • Minimal suspicious dependencies
echo.
echo The executable is ready for distribution and should have
echo reduced likelihood of antivirus false positives.
echo.

REM Calculate and display file hash
echo Calculating SHA-256 hash for verification...
python -c "import hashlib; f=open('Bashanddash.exe','rb'); print('SHA-256:', hashlib.sha256(f.read()).hexdigest()); f.close()"
echo.

echo Build process complete!
pause
