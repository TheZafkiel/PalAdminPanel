@echo off
setlocal
chcp 65001 >nul
set "PYTHONHOME="
set "PYTHONPATH="
set "VIRTUAL_ENV="
set "__PYVENV_LAUNCHER__="
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
set "VENV_PY=.runtime\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [1/4] Creating isolated Python 3.11 runtime...
    py -3.11 -m venv .runtime
    if errorlevel 1 goto :error
)

"%VENV_PY%" -c "import encodings" >nul 2>&1
if errorlevel 1 (
    echo The isolated Python runtime is invalid: .runtime
    echo Rename or remove .runtime, then run this script again.
    goto :error
)

echo [2/4] Checking required components...
"%VENV_PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :error

if not exist "config.json" (
    echo [3/4] First-time setup...
    "%VENV_PY%" setup_config.py
    if errorlevel 1 goto :error
) else (
    echo [3/4] Existing configuration found.
)

"%VENV_PY%" configure_rest.py --ensure
if errorlevel 1 goto :error

echo [4/4] Starting PalAdminPanel...
echo Open on this computer: http://127.0.0.1:5000
echo Press Ctrl+C to stop.
"%VENV_PY%" app.py
if errorlevel 1 goto :error
goto :end

:error
set "EXIT_CODE=%errorlevel%"
echo.
echo Startup failed with exit code %EXIT_CODE%. Review the message above.
exit /b %EXIT_CODE%

:end
endlocal
