@echo off
echo 🚀 Starting FastAPI Backend...
echo ================================

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause


