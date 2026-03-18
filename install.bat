@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================
echo   Illustrator MCP Server - 설치 프로그램
echo ============================================
echo.

:: ==========================================
:: [1] Python 탐색
:: ==========================================
set "PYTHON_CMD="

:: 1순위: py 런처
py -3 --version > nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :python_found
)

:: 2순위: python
python --version > nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "_PYCHECK=%%v"
    echo !_PYCHECK! | findstr /b "3." > nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
        goto :python_found
    )
)

:: 3순위: python3
python3 --version > nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python3"
    goto :python_found
)

:: 4순위: 일반적인 설치 경로 직접 탐색
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%PROGRAMFILES%\Python313\python.exe"
    "%PROGRAMFILES%\Python312\python.exe"
    "%PROGRAMFILES%\Python311\python.exe"
    "%PROGRAMFILES%\Python310\python.exe"
) do (
    if exist %%p (
        set "PYTHON_CMD=%%~p"
        goto :python_found
    )
)

:: Python을 찾지 못한 경우
echo [오류] Python을 찾을 수 없습니다.
echo.
echo 자동으로 Python을 설치하시겠습니까? (Y/N)
set /p "AUTO_INSTALL="
if /i "!AUTO_INSTALL!"=="Y" (
    winget --version > nul 2>&1
    if errorlevel 1 (
        echo [오류] winget을 사용할 수 없습니다.
        echo        Python 3.11 이상을 직접 설치해주세요: https://www.python.org/downloads/
        echo        설치 시 "Add Python to PATH" 옵션을 반드시 체크해주세요.
        pause
        exit /b 1
    )
    echo Python 3.12를 설치합니다...
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [오류] Python 자동 설치에 실패했습니다.
        echo        Python 3.11 이상을 직접 설치해주세요: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    :: 설치 직후 PATH 반영이 안 되므로 직접 경로 탐색
    for %%p in (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%PROGRAMFILES%\Python312\python.exe"
    ) do (
        if exist %%p (
            set "PYTHON_CMD=%%~p"
            goto :python_found
        )
    )
    echo [오류] Python 설치는 완료되었으나 경로를 찾을 수 없습니다.
    echo        명령 프롬프트를 닫고 다시 열어서 install.bat을 실행해주세요.
    pause
    exit /b 1
) else (
    echo Python 3.11 이상을 설치해주세요: https://www.python.org/downloads/
    echo 설치 시 "Add Python to PATH" 옵션을 반드시 체크해주세요.
    pause
    exit /b 1
)

:python_found
:: Python 버전 확인
for /f "tokens=2" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set "PYVER=%%i"
echo [OK] Python %PYVER% 발견 (%PYTHON_CMD%)

:: 버전 3.10 이상인지 검증
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    if %%a LSS 3 (
        echo [오류] Python 3.10 이상이 필요합니다. 현재: %PYVER%
        pause
        exit /b 1
    )
    if %%a EQU 3 if %%b LSS 10 (
        echo [오류] Python 3.10 이상이 필요합니다. 현재: %PYVER%
        pause
        exit /b 1
    )
)

:: ==========================================
:: [2] 레포지토리 확인
:: ==========================================
set "SCRIPT_DIR=%~dp0"

:: install.bat이 레포 안에 있는지 확인
if exist "%SCRIPT_DIR%pyproject.toml" (
    set "REPO_DIR=%SCRIPT_DIR%"
    echo [OK] 레포지토리 확인됨
    goto :repo_ready
)

:: 레포가 없으면 다운로드 필요
echo [INFO] 레포지토리를 다운로드합니다...
echo.

set "REPO_DIR=%USERPROFILE%\illustrator-mcp"
set "ZIP_URL=https://github.com/slashprint/illustrator-mcp/archive/refs/heads/main.zip"
set "ZIP_FILE=%TEMP%\illustrator-mcp.zip"
set "ZIP_EXTRACT=%TEMP%\illustrator-mcp-extract"

:: 기존 설치가 있으면 삭제 후 새로 다운로드
if exist "!REPO_DIR!\pyproject.toml" (
    echo 기존 설치 폴더를 발견했습니다. 최신 버전으로 교체합니다...
    rmdir /s /q "!REPO_DIR!" 2>nul
)

:: PowerShell로 ZIP 다운로드
echo ZIP 파일을 다운로드합니다...
powershell -NoProfile -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%ZIP_URL%' -OutFile '%ZIP_FILE%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
    echo [오류] 다운로드에 실패했습니다.
    echo        네트워크 연결을 확인해주세요.
    pause
    exit /b 1
)

:: 압축 해제
echo 압축을 해제합니다...
if exist "%ZIP_EXTRACT%" rmdir /s /q "%ZIP_EXTRACT%"
powershell -NoProfile -Command "try { Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%ZIP_EXTRACT%' -Force } catch { exit 1 }"
if errorlevel 1 (
    echo [오류] 압축 해제에 실패했습니다.
    del "%ZIP_FILE%" 2>nul
    pause
    exit /b 1
)

:: GitHub ZIP은 폴더명이 "illustrator-mcp-main"으로 풀림 → 이름 변경
move "%ZIP_EXTRACT%\illustrator-mcp-main" "!REPO_DIR!" > nul
if errorlevel 1 (
    echo [오류] 폴더 이동에 실패했습니다.
    pause
    exit /b 1
)

:: 임시 파일 정리
del "%ZIP_FILE%" 2>nul
rmdir /s /q "%ZIP_EXTRACT%" 2>nul

echo [OK] 다운로드 완료: !REPO_DIR!
set "REPO_DIR=!REPO_DIR!\"

:repo_ready
cd /d "%REPO_DIR%"

:: ==========================================
:: [3] 가상 환경 생성
:: ==========================================
echo.
echo [1/4] 가상 환경을 생성합니다...
if exist ".venv" (
    echo       기존 가상 환경을 삭제합니다...
    rmdir /s /q ".venv"
)
!PYTHON_CMD! -m venv .venv
if errorlevel 1 (
    echo [오류] 가상 환경 생성에 실패했습니다.
    pause
    exit /b 1
)
echo       완료.

:: venv 내 Python/pip 경로 설정
set "VENV_PYTHON=%REPO_DIR%.venv\Scripts\python.exe"
set "VENV_PIP=%REPO_DIR%.venv\Scripts\pip.exe"

:: ==========================================
:: [4] 의존성 설치
:: ==========================================
echo.
echo [2/4] 의존성을 설치합니다...
call "%VENV_PIP%" install --upgrade pip > nul 2>&1
call "%VENV_PIP%" install -e .
if errorlevel 1 (
    echo [오류] 의존성 설치에 실패했습니다.
    echo        네트워크 연결을 확인해주세요.
    pause
    exit /b 1
)
echo       완료.

:: ==========================================
:: [5] Claude Desktop 설정
:: ==========================================
echo.
echo [3/4] Claude Desktop 설정을 확인합니다...

set "CLAUDE_CONFIG_DIR=%APPDATA%\Claude"
set "CLAUDE_CONFIG=%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"
set "SERVER_PATH=%REPO_DIR%illustrator\server.py"

:: Claude Desktop 설치 여부 확인
if not exist "%CLAUDE_CONFIG_DIR%" (
    echo [경고] Claude Desktop이 설치되어 있지 않거나 아직 실행된 적이 없습니다.
    echo        Claude Desktop을 설치해주세요: https://claude.ai/download
    echo        설치 후 한 번 실행한 다음 이 스크립트를 다시 실행해주세요.
    echo.
    goto :skip_config_merge
)

:: Python 스크립트로 JSON 안전 병합
echo [4/4] Claude Desktop 설정에 등록합니다...

:: delayed expansion을 끄고 Python 스크립트 작성 (! 문자 충돌 방지)
setlocal disabledelayedexpansion

set "MERGE_SCRIPT=%TEMP%\illustrator_mcp_merge.py"

(
echo import json, os, sys, shutil
echo.
echo config_path = sys.argv[1]
echo python_path = sys.argv[2]
echo server_path = sys.argv[3]
echo.
echo new_entry = {
echo     "command": python_path.replace("\\", "/"),
echo     "args": [server_path.replace("\\", "/")]
echo }
echo.
echo config = {}
echo if os.path.exists(config_path):
echo     try:
echo         with open(config_path, "r", encoding="utf-8") as f:
echo             content = f.read().strip()
echo             if content:
echo                 config = json.loads(content)
echo     except (json.JSONDecodeError, Exception) as e:
echo         backup = config_path + ".backup"
echo         shutil.copy2(config_path, backup)
echo         print(f"[경고] 기존 설정 파일이 손상되어 백업했습니다: {backup}")
echo         config = {}
echo.
echo if "mcpServers" not in config:
echo     config["mcpServers"] = {}
echo.
echo config["mcpServers"]["illustrator"] = new_entry
echo.
echo os.makedirs(os.path.dirname(config_path), exist_ok=True)
echo.
echo with open(config_path, "w", encoding="utf-8") as f:
echo     json.dump(config, f, indent=2, ensure_ascii=False)
echo.
echo print("[OK] Claude Desktop 설정이 업데이트되었습니다.")
echo print(f"     파일: {config_path}")
echo servers = list(config["mcpServers"].keys())
echo print(f"     등록된 MCP 서버: {', '.join(servers)}")
) > "%MERGE_SCRIPT%"

endlocal

:: 병합 스크립트 실행
"%REPO_DIR%.venv\Scripts\python.exe" "%TEMP%\illustrator_mcp_merge.py" "%APPDATA%\Claude\claude_desktop_config.json" "%REPO_DIR%.venv\Scripts\python.exe" "%REPO_DIR%illustrator\server.py"

if errorlevel 1 (
    echo [경고] 자동 설정에 실패했습니다. 수동으로 설정해주세요.
    goto :skip_config_merge
)

:: 임시 파일 정리
del "%TEMP%\illustrator_mcp_merge.py" 2>nul
goto :install_done

:skip_config_merge
:: 자동 설정 실패 시 수동 설정 안내
set "PYTHON_PATH_JSON=%REPO_DIR%.venv\Scripts\python.exe"
set "SERVER_PATH_JSON=%REPO_DIR%illustrator\server.py"
set "PYTHON_PATH_JSON=%PYTHON_PATH_JSON:\=/%"
set "SERVER_PATH_JSON=%SERVER_PATH_JSON:\=/%"

set "CONFIG_FILE=%REPO_DIR%claude_config_snippet.json"
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
echo ============================================
echo   수동 설정 안내
echo ============================================
echo.
echo 아래 내용을 Claude Desktop 설정 파일에 추가해주세요:
echo.
echo   파일 위치: %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo   "mcpServers" 안에 다음을 추가:
echo.
echo   "illustrator": {
echo     "command": "%PYTHON_PATH_JSON%",
echo     "args": ["%SERVER_PATH_JSON%"]
echo   }
echo.
echo   설정 예시 파일: %CONFIG_FILE%
echo.

:install_done
echo.
echo ============================================
echo   설치가 완료되었습니다!
echo ============================================
echo.
echo 다음 단계:
echo   1. Adobe Illustrator를 실행하세요
echo   2. Claude Desktop을 재시작하세요
echo   3. Claude에게 말해보세요: "현재 Illustrator 문서를 보여줘"
echo.
echo ============================================
echo.

pause
