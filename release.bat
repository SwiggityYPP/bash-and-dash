@echo off
echo ================================
echo  Bash and Dash Release Tool
echo ================================
echo.

if "%1"=="" (
    echo Usage: release.bat [patch^|minor^|major^|version]
    echo.
    echo Examples:
    echo   release.bat patch     ^(1.0.0 -^> 1.0.1^)
    echo   release.bat minor     ^(1.0.0 -^> 1.1.0^)
    echo   release.bat major     ^(1.0.0 -^> 2.0.0^)
    echo   release.bat 1.2.3     ^(set specific version^)
    echo.
    pause
    exit /b 1
)

echo Starting release process for: %1
echo.

python update_version.py %1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Release process completed!
    echo The new version will be built automatically on GitHub.
    echo Check: https://github.com/YourUsername/bash-and-dash/actions
) else (
    echo.
    echo ❌ Release process failed!
)

echo.
pause
