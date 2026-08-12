@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo  Srinivasa Technology - Database Backup
echo ============================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where mysqldump 2^>nul') do set "MYSQLDUMP=%%i"
if not defined MYSQLDUMP (
    for %%i in ("C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe") do if exist "%%~i" set "MYSQLDUMP=%%~i"
)
if not defined MYSQLDUMP (
    echo [ERROR] mysqldump not found. Install MySQL 8 and add it to PATH.
    pause
    exit /b 1
)

set "DB_NAME="
set "DB_USER="
set "DB_PASSWORD="

for /f "tokens=1,2 delims==" %%a in (.env) do (
    set "line=%%a=%%b"
    set "key=%%a"
    if "!key!"=="DB_NAME" set "DB_NAME=%%b"
    if "!key!"=="DB_USER" set "DB_USER=%%b"
    if "!key!"=="DB_PASSWORD" set "DB_PASSWORD=%%b"
)

if "%DB_NAME%"=="" (
    echo [ERROR] Could not read .env. Run this from the project root.
    pause
    exit /b 1
)

rem Create daily / weekly / monthly folders
set "ROOT=backups"
if not exist "%ROOT%\daily" mkdir "%ROOT%\daily"
if not exist "%ROOT%\weekly" mkdir "%ROOT%\weekly"
if not exist "%ROOT%\monthly" mkdir "%ROOT%\monthly"

rem Decide folder based on day of week / date
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "DD=%%c"
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value 2^>nul ^| find "="') do set "DT=%%i"
if not defined DT for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "DT=%%i"
set "STAMP=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%_%DT:~8,6%"

set "SUBDIR=daily"
set "DAYNUM=1"
for /f %%i in ('powershell -NoProfile -Command "(Get-Date).DayOfWeek.value__"') do set "DAYNUM=%%i"
if "%DAYNUM%"=="0" set "SUBDIR=weekly"
for /f %%i in ('powershell -NoProfile -Command "if((Get-Date).Day -eq 1){'monthly'}"') do if not "%%i"=="" set "SUBDIR=%%i"

set "FILE=%ROOT%\%SUBDIR%\srinivasa_backup_%STAMP%.sql"

echo Backing up database '%DB_NAME%' to %FILE% ...
"%MYSQLDUMP%" --single-transaction --routines --triggers -h127.0.0.1 -P3306 -u"%DB_USER%" -p"%DB_PASSWORD%" "%DB_NAME%" > "%FILE%"

if errorlevel 1 (
    echo [ERROR] Backup failed. Check DB credentials in .env and that MySQL is running.
    pause
    exit /b 1
)

echo Backing up media files ...
powershell -NoProfile -Command "Compress-Archive -Path 'media' -DestinationPath '%ROOT%\%SUBDIR%\srinivasa_media_%STAMP%.zip' -Force"

echo.
echo [OK] Backup completed:
echo      %FILE%
echo      %ROOT%\%SUBDIR%\srinivasa_media_%STAMP%.zip
echo.
pause
