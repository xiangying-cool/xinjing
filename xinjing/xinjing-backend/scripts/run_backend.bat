@echo off
setlocal

REM Usage:
REM   scripts\run_backend.bat [host] [port] [env_file]
REM Example:
REM   scripts\run_backend.bat 0.0.0.0 8000 .env.test

set "HOST=%~1"
if "%HOST%"=="" set "HOST=0.0.0.0"

set "PORT=%~2"
if "%PORT%"=="" set "PORT=8000"

set "ENV_FILE=%~3"
if "%ENV_FILE%"=="" set "ENV_FILE=.env.test"

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "BACKEND_ROOT=%%~fI"
set "PYTHON_EXE=%BACKEND_ROOT%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Python not found: "%PYTHON_EXE%"
  echo [HINT] Please create venv first: python -m venv .venv
  exit /b 1
)

pushd "%BACKEND_ROOT%"
set "XJ_ENV_FILE=%ENV_FILE%"

echo [INFO] Backend root: %BACKEND_ROOT%
echo [INFO] XJ_ENV_FILE=%XJ_ENV_FILE%
echo [INFO] Starting backend at http://%HOST%:%PORT%
echo [INFO] Press Ctrl+C to stop backend.

"%PYTHON_EXE%" -m uvicorn app.main:app --host %HOST% --port %PORT% --reload --reload-dir app
set "EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %EXIT_CODE%
