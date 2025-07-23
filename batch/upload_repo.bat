@echo off
echo Uploading changes to repository...

:: تنظیم مسیر پوشه مخزن (محلی که پروژه کلون شده)
set "REPO_DIR=C:\Users\homay\Downloads\med"
set "COMMIT_MESSAGE=Auto-upload changes on %date% %time%"

:: بررسی وجود پوشه مخزن
if not exist "%REPO_DIR%" (
    echo Error: Repository directory not found at %REPO_DIR%. Please clone the repository first.
    pause
    exit /b
)

cd /d "%REPO_DIR%"

:: اضافه کردن تمام تغییرات
git add .

:: کامیت تغییرات
git commit -m "%COMMIT_MESSAGE%"

:: پوش کردن به مخزن
git push origin main

if %ERRORLEVEL%==0 (
    echo Changes uploaded successfully!
) else (
    echo Error occurred while uploading. Check your Git configuration or network.
)

pause