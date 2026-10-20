@echo off
setlocal
chcp 65001 >nul
set "PYTHONHOME="
set "PYTHONPATH="
set "VIRTUAL_ENV="
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
if not exist ".runtime\Scripts\python.exe" py -3.11 -m venv .runtime
".runtime\Scripts\python.exe" prepare_server_rest.py
exit /b %errorlevel%
