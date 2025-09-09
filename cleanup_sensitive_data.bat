@echo off
echo 🔒 SECURITY CLEANUP SCRIPT
echo ==========================
echo.
echo This script will remove all sensitive data before uploading to GitHub
echo.

echo ⚠️  WARNING: This will delete all session configurations and credentials!
echo.
set /p confirm="Are you sure you want to continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo 🗑️  Removing sensitive configuration files...

REM Remove session config files
if exist "backend\session_*_config.json" (
    del "backend\session_*_config.json"
    echo ✅ Removed session config files
) else (
    echo ℹ️  No session config files found
)

if exist "backend\sessions_config.json" (
    del "backend\sessions_config.json"
    echo ✅ Removed sessions config file
) else (
    echo ℹ️  No sessions config file found
)

REM Remove database files
if exist "backend\freelancer_bot.db" (
    del "backend\freelancer_bot.db"
    echo ✅ Removed database file
) else (
    echo ℹ️  No database file found
)

if exist "freelancer_bot.db" (
    del "freelancer_bot.db"
    echo ✅ Removed root database file
) else (
    echo ℹ️  No root database file found
)

REM Remove Excel log files
if exist "backend\bid_log.xlsx" (
    del "backend\bid_log.xlsx"
    echo ✅ Removed bid log file
) else (
    echo ℹ️  No bid log file found
)

if exist "bid_log.xlsx" (
    del "bid_log.xlsx"
    echo ✅ Removed root bid log file
) else (
    echo ℹ️  No root bid log file found
)

REM Create clean .env file if it doesn't exist
if not exist ".env" (
    if exist "env.example" (
        copy "env.example" ".env"
        echo ✅ Created clean .env file from example
    ) else (
        echo ⚠️  No env.example file found
    )
) else (
    echo ℹ️  .env file already exists
)

echo.
echo 🎉 Security cleanup completed!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your actual API keys
echo 2. Test the application to ensure it works
echo 3. Commit and push to GitHub
echo.
echo ⚠️  Remember: Never commit real API keys or credentials!
echo.
pause


