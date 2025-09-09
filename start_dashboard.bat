@echo off
echo 🤖 Freelancer Bot Dashboard
echo ================================

echo.
echo 📋 Available options:
echo 1. Run backend only (FastAPI)
echo 2. Run frontend only (React)
echo 3. Run bot directly
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo 🚀 Starting FastAPI backend...
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) else if "%choice%"=="2" (
    echo 🎨 Starting React frontend...
    cd frontend
    npm start
) else if "%choice%"=="3" (
    echo 🤖 Running bot directly...
    python main.py
) else (
    echo ❌ Invalid choice
)

pause

