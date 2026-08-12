@echo off
setlocal
cd /d "%~dp0"

echo Stopping the Srinivasa Technology server...

rem Find the runserver / waitress python process started from this folder and stop it.
powershell -NoProfile -Command ^
  "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manage.py.*runserver' -and $_.ExecutablePath -match 'Inventory-Django' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; Write-Output ('Stopped PID ' + $_.ProcessId) }"

echo Server stopped (if it was running).
pause
