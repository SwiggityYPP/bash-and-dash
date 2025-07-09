@echo off
REM Bash and Dash Game Log Analyzer - Debug Build Script
REM This script creates a debug version with error tracebacks enabled

echo ================================================================
echo  Bash and Dash Game Log Analyzer - Debug Build
echo  Building executable with error tracebacks enabled...
echo ================================================================
echo.

REM Check if PyInstaller is available
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo FAILED: Could not install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist\Bashanddash-debug.exe" del "dist\Bashanddash-debug.exe" 2>nul

REM Build the debug executable
echo.
echo Building debug executable...
echo Command: pyinstaller Bashanddash-debug.spec --clean --noconfirm
echo.

pyinstaller Bashanddash-debug.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\Bashanddash-debug.exe" (
    echo.
    echo ================================================================
    echo  BUILD SUCCESSFUL!
    echo ================================================================
    echo.
    echo Debug executable created: dist\Bashanddash-debug.exe
    echo.
    
    REM Copy to root directory for easy access
    copy "dist\Bashanddash-debug.exe" "Bashanddash-debug.exe" >nul 2>&1
    if exist "Bashanddash-debug.exe" (
        echo Also copied to: Bashanddash-debug.exe
        echo.
        
        REM Show file information
        for %%i in ("Bashanddash-debug.exe") do (
            echo File size: %%~zi bytes
            echo Created: %%~ti
        )
    )
    
    echo.
    echo This debug version will show detailed error messages if issues occur.
    echo Run it from command prompt to see any error output.
    echo.
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo  BUILD FAILED!
    echo ================================================================
    echo.
    echo The executable was not created. Check the output above for errors.
    echo.
    echo Common issues:
    echo - Missing dependencies (install with: pip install -r requirements-build.txt)
    echo - Antivirus blocking the build process
    echo - Insufficient disk space
    echo - Python path issues
    echo.
    echo ================================================================
)

echo.
echo Press any key to exit...
pause >nul
