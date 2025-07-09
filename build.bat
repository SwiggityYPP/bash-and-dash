@echo off
echo Building Bash and Dash...

REM Clean previous builds
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist Bashanddash.exe del Bashanddash.exe 2>nul

REM Build the executable
C:/Users/User/AppData/Local/Programs/Python/Python313/python.exe -m PyInstaller --clean Bashanddash.spec

REM Copy executable to root directory
if exist dist\Bashanddash.exe (
    copy dist\Bashanddash.exe Bashanddash.exe >nul
    echo Build complete! Executable: Bashanddash.exe
) else (
    echo Build failed! Check for errors above.
)

pause
