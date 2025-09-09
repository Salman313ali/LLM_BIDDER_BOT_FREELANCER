@echo off
echo 🚀 Freelancer Bot Setup
echo ======================

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing Node.js dependencies...
cd frontend
npm install
cd ..

echo.
echo Creating environment file...
if not exist .env (
    if exist env.example (
        copy env.example .env
        echo ✅ Created .env file from example
        echo ⚠️  Please edit .env file with your actual API keys
    ) else (
        echo ⚠️  No env.example file found, you'll need to create .env manually
    )
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run 'start_backend.bat' to start the backend
echo 3. Run 'start_frontend.bat' to start the frontend
echo 4. Open http://localhost:3000 in your browser
echo.
pause

