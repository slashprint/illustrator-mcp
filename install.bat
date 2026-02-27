@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================
echo   Illustrator MCP Server - Installer
echo ============================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% found

:: Check Python version is 3.10+
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    if %%a LSS 3 (
        echo [ERROR] Python 3.10+ required. Found: %PYVER%
        pause
        exit /b 1
    )
    if %%a EQU 3 if %%b LSS 10 (
        echo [ERROR] Python 3.10+ required. Found: %PYVER%
        pause
        exit /b 1
    )
)

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo [1/4] Creating virtual environment...
if exist ".venv" (
    echo       Virtual environment already exists, removing...
    rmdir /s /q ".venv"
)
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo       Done.

echo.
echo [2/4] Installing dependencies...
call .venv\Scripts\pip.exe install --upgrade pip > nul 2>&1
call .venv\Scripts\pip.exe install -e .
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo       Done.

echo.
echo [3/4] Generating Claude Desktop configuration...

:: Get full path to Python in venv
set "PYTHON_PATH=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "SERVER_PATH=%SCRIPT_DIR%illustrator\server.py"

:: Replace backslashes with forward slashes for JSON
set "PYTHON_PATH_JSON=%PYTHON_PATH:\=/%"
set "SERVER_PATH_JSON=%SERVER_PATH:\=/%"

:: Create config snippet
echo.
echo ============================================
echo   Add this to your Claude Desktop config:
echo ============================================
echo.
echo   File location:
echo   %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo   Configuration to add inside "mcpServers":
echo.
echo   "illustrator": {
echo     "command": "%PYTHON_PATH_JSON%",
echo     "args": ["%SERVER_PATH_JSON%"]
echo   }
echo.
echo ============================================

:: Save config to file for easy copy
set "CONFIG_FILE=%SCRIPT_DIR%claude_config_snippet.json"
(
echo {
echo   "mcpServers": {
echo     "illustrator": {
echo       "command": "%PYTHON_PATH_JSON%",
echo       "args": ["%SERVER_PATH_JSON%"]
echo     }
echo   }
echo }
) > "%CONFIG_FILE%"

echo.
echo [4/4] Configuration saved to:
echo       %CONFIG_FILE%
echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Open Claude Desktop config file:
echo      %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo   2. Add the configuration shown above
echo      (or copy from claude_config_snippet.json)
echo.
echo   3. Restart Claude Desktop
echo.
echo   4. Make sure Adobe Illustrator is running
echo.
echo   5. Try asking Claude: "Show me the current Illustrator document"
echo.
echo ============================================
echo.

pause
