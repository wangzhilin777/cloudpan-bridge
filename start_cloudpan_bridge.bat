@echo off
cd /d "%~dp0"
where pwsh >nul 2>nul
if %errorlevel%==0 (
  start "" pwsh -NoExit -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_cloudpan_bridge.ps1"
) else (
  start "" powershell -NoExit -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_cloudpan_bridge.ps1"
)
