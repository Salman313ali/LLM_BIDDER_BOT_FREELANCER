# Freelancer.com Bidding Bot

An intelligent automated bidding bot for Freelancer.com with a modern web dashboard. The bot uses AI to analyze projects, match them with your service offerings, and place competitive bids automatically.

## 🚀 Features

- **AI-Powered Project Analysis**: Uses Groq LLM to analyze projects and determine if they match your services
- **Multi-Session Support**: Run multiple bot instances for different Freelancer accounts simultaneously
- **Customizable Bidding**: Configure service offerings, bid writing style, portfolio links, and signatures
- **Real-time Dashboard**: Modern React-based web interface to monitor bot activity
- **Session Management**: Secure switching between different Freelancer accounts
- **Bid Tracking**: Comprehensive logging and tracking of all placed bids
- **Project Filtering**: Advanced filtering based on skills, languages, currencies, and countries

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js
- **Database**: SQLite
- **AI**: Groq LLM (Qwen3-32b)
- **API**: Freelancer.com SDK

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Freelancer.com account with API access
- Groq API key

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd freelancer-bot
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
cd backend
python main.py
```

### 3. Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start the development server
npm start
```

## ⚙️ Configuration

### 1. API Keys
- **Freelancer OAuth Token**: Get from your Freelancer.com account settings
- **Groq API Key**: Get from [Groq Console](https://console.groq.com/)

### 2. Service Configuration
Configure your service offerings, bid writing style, portfolio links, and signature through the web dashboard.

### 3. Session Management
Create multiple sessions for different Freelancer accounts with their own configurations.

## 🚀 Usage

1. **Access the Dashboard**: Open `http://localhost:3000` in your browser
2. **Configure Settings**: Go to Configuration tab and set up your API keys and preferences
3. **Create Sessions**: Create sessions for different Freelancer accounts
4. **Start Bot**: Select a session and start the bot
5. **Monitor Progress**: Watch real-time progress in the dashboard

## 📁 Project Structure

```
freelancer-bot/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   └── freelancer_bot.db   # SQLite database
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── package.json
├── src/                    # Core bot logic
│   ├── bot.py             # Main bot class
│   ├── ai_service.py      # AI analysis service
│   ├── freelancer_service.py # Freelancer API service
│   ├── session_manager.py # Session management
│   ├── config_manager.py  # Configuration management
│   └── database.py        # Database operations
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## 🔒 Security

- **API Keys**: Never commit API keys to version control
- **Configuration**: Session-specific configurations are stored locally
- **Database**: SQLite database contains only project and bid data

### ⚠️ **IMPORTANT SECURITY NOTICE**

**BEFORE UPLOADING TO GITHUB:**

1. **Remove all session config files**:
   ```bash
   rm backend/session_*_config.json
   rm backend/sessions_config.json
   ```

2. **Create a clean .env file**:
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

3. **Never commit real credentials** - The `.gitignore` file protects sensitive data, but always double-check before pushing to GitHub.

## 📊 Monitoring

The dashboard provides real-time monitoring of:
- Bot status and progress
- Projects found and analyzed
- Bids placed and their status
- Error logs and debugging information
- Session-specific statistics

## 🐛 Troubleshooting

### Common Issues

1. **Bot not starting**: Check API keys and network connection
2. **No projects found**: Verify search filters and skill IDs
3. **Bid failures**: Check Freelancer account status and bid limits
4. **Session errors**: Ensure proper configuration for each session

### Logs
Check the dashboard logs section for detailed error information and debugging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and personal use only. Please ensure compliance with Freelancer.com's terms of service.

## ⚠️ Disclaimer

This bot is designed to assist with bidding on Freelancer.com. Users are responsible for:
- Complying with Freelancer.com's terms of service
- Ensuring all bids are appropriate and professional
- Monitoring bot activity and results
- Maintaining their Freelancer.com account in good standing

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the dashboard
3. Create an issue in the repository

---

**Happy Bidding! 🎯**