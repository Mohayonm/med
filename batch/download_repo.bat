@echo off
echo Downloading or updating repository...

:: تنظیم مسیر پوشه مقصد (می‌توانید تغییر دهید)
set "REPO_DIR=C:\Users\homay\Downloads\med\new"
set "REPO_URL=https://github.com/mohayonm/medical.git"

:: بررسی وجود پوشه
if exist "%REPO_DIR%" (
    cd /d "%REPO_DIR%"
    echo Updating existing repository...
    git pull origin main
) else (
    echo Cloning repository...
    git clone %REPO_URL% "%REPO_DIR%"
)

echo Done!
pause