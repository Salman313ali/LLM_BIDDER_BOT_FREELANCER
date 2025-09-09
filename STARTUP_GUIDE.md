# 🚀 Freelancer Bot Startup Guide

## Quick Start Options

### Option 1: Use the Batch Files (Recommended for Windows)

1. **Start Backend Only:**
   ```
   Double-click: start_backend.bat
   ```

2. **Start Frontend Only:**
   ```
   Double-click: start_frontend.bat
   ```

3. **Start Bot Directly:**
   ```
   Double-click: start_bot.bat
   ```

### Option 2: Manual Commands

#### 1. Start the Backend (FastAPI)
```bash
# Open Command Prompt/Terminal in the project root
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Start the Frontend (React)
```bash
# Open a NEW Command Prompt/Terminal in the project root
cd frontend
npm start
```

#### 3. Run Bot Directly
```bash
# Open Command Prompt/Terminal in the project root
python main.py
```

## Complete Setup (Full Dashboard)

To run the complete dashboard with both backend and frontend:

### Terminal 1 - Backend:
```bash
cd "C:\freelancer\bot\test_bot - Copy"
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Frontend:
```bash
cd "C:\freelancer\bot\test_bot - Copy"
cd frontend
npm start
```

## Access Points

- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Troubleshooting

### Backend Issues:
- Make sure you're in the `backend` directory when running uvicorn
- Check that all dependencies are installed: `pip install -r backend/requirements.txt`
- Verify Python virtual environment is activated

### Frontend Issues:
- Make sure you're in the `frontend` directory when running npm start
- Check that Node.js dependencies are installed: `npm install`
- Clear npm cache if needed: `npm cache clean --force`

### Bot Issues:
- Make sure you're in the project root directory
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your API keys are set in `src/config.py`

## Environment Setup

1. **Activate Virtual Environment:**
   ```bash
   my_env\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

## Configuration

Before running the bot, make sure to set your API keys in `src/config.py`:

```python
OAUTH_TOKEN = 'your_freelancer_oauth_token'
GROQ_API_KEY = 'your_groq_api_key'
```

## Testing the Setup

Run the test script to verify everything is working:

```bash
python test_setup.py
```

## Common Commands

| Action | Command |
|--------|---------|
| Start Backend | `cd backend && python -m uvicorn main:app --reload` |
| Start Frontend | `cd frontend && npm start` |
| Run Bot | `python main.py` |
| Test Setup | `python test_setup.py` |
| Install Backend Deps | `pip install -r backend/requirements.txt` |
| Install Frontend Deps | `cd frontend && npm install` |

## Notes

- The backend runs on port 8000
- The frontend runs on port 3000
- Both need to be running for the full dashboard experience
- The bot can run independently without the dashboard
- Use Ctrl+C to stop any running process





