@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Srinivasa Technology - Traceability System
echo ============================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Run: python -m venv .venv
    echo Then:  .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo [1/3] Running migrations...
.venv\Scripts\python.exe manage.py migrate || goto :error

echo [2/3] Collecting static files...
.venv\Scripts\python.exe manage.py collectstatic --noinput || goto :error

echo [3/3] Starting server on 0.0.0.0:8000 (LAN access)
echo Access from other PCs:  http://SERVER-IP:8000
echo Press Ctrl+C to stop.
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000 --noreload

goto :eof

:error
echo.
echo [ERROR] Startup failed. See messages above.
pause
exit /b 1
