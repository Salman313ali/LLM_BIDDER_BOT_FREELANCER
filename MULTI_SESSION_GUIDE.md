# 🔄 Multi-Session Guide

## Overview

The Freelancer Bot now supports **multiple concurrent sessions**, allowing you to run different bot instances simultaneously for different Freelancer accounts. This is perfect for managing multiple accounts securely and efficiently.

## Key Features

### ✅ **Multiple Account Support**
- Create separate sessions for each Freelancer account
- Each session has its own OAuth token and configuration
- Run multiple bots simultaneously without conflicts

### ✅ **Secure Session Management**
- Each session is isolated with its own configuration
- API keys are stored securely per session
- No cross-contamination between accounts

### ✅ **Individual Monitoring**
- Track progress for each session separately
- View statistics and logs per account
- Start/stop individual bots independently

### ✅ **Customizable Per Session**
- Different service offerings per account
- Unique bid writing styles
- Separate portfolio links and signatures
- Individual bot settings (bid limits, search parameters)

## How to Use Multi-Sessions

### 1. **Create Your First Session**

1. **Go to the Sessions page** in the dashboard
2. **Click "New Session"**
3. **Fill in the session details**:
   - **Session Name**: Give it a descriptive name (e.g., "Main Account", "Secondary Account")
   - **OAuth Token**: Your Freelancer.com OAuth token for this account
   - **Groq API Key**: Your Groq API key (can be shared across sessions)
   - **Service Offerings**: What services this account should bid on
   - **Bid Writing Style**: How bids should be written for this account
   - **Portfolio Links**: Portfolio links specific to this account
   - **Signature**: Your name/signature for this account

### 2. **Create Additional Sessions**

Repeat the process for each additional Freelancer account you want to manage.

### 3. **Manage Sessions**

- **View All Sessions**: See all your sessions on the Sessions page
- **Start/Stop Individual Bots**: Control each bot independently
- **Edit Session Settings**: Update configuration for any session
- **Delete Sessions**: Remove sessions you no longer need

### 4. **Monitor Progress**

- **Real-time Status**: See which bots are running
- **Individual Statistics**: Track bids and projects per session
- **Session-specific Logs**: View logs for each account separately

## Example Setup

### Session 1: "Web Development Account"
- **OAuth Token**: `your_web_dev_token`
- **Service Offerings**: WordPress, React, E-commerce development
- **Bid Writing Style**: Professional, technical, solution-focused
- **Portfolio**: GitHub, web development portfolio
- **Signature**: "John Smith - Web Developer"

### Session 2: "Graphic Design Account"
- **OAuth Token**: `your_design_token`
- **Service Offerings**: Logo design, branding, UI/UX
- **Bid Writing Style**: Creative, enthusiastic, visual-focused
- **Portfolio**: Behance, Dribbble, design galleries
- **Signature**: "Sarah Johnson - Graphic Designer"

### Session 3: "Writing Account"
- **OAuth Token**: `your_writing_token`
- **Service Offerings**: Content writing, copywriting, blog posts
- **Bid Writing Style**: Conversational, persuasive, results-oriented
- **Portfolio**: Writing samples, published articles
- **Signature**: "Mike Davis - Content Writer"

## Best Practices

### 🔒 **Security**
- **Use different OAuth tokens** for each account
- **Keep API keys secure** and don't share them
- **Regularly rotate tokens** for security
- **Use strong, unique session names**

### ⚙️ **Configuration**
- **Customize service offerings** to match each account's strengths
- **Set appropriate bid limits** per account
- **Use different signatures** for each account
- **Tailor bid writing styles** to each account's voice

### 📊 **Monitoring**
- **Check session status regularly**
- **Monitor bid success rates** per account
- **Review logs** for any issues
- **Adjust settings** based on performance

### 🚀 **Performance**
- **Don't run too many sessions** simultaneously (recommended: 2-3 max)
- **Set reasonable bid limits** to avoid overwhelming accounts
- **Monitor system resources** when running multiple bots
- **Use different wait times** to avoid conflicts

## Technical Details

### **Session Isolation**
- Each session has its own configuration file
- Bot instances run in separate threads
- Database entries are tagged with session IDs
- No shared state between sessions

### **Resource Management**
- Each bot runs in its own thread
- Memory usage scales with number of active sessions
- Database connections are shared efficiently
- API rate limits apply per OAuth token

### **Data Storage**
- Session configurations: `sessions_config.json`
- Individual session configs: `session_{id}_config.json`
- Database entries include session IDs
- Logs are tagged with session information

## Troubleshooting

### **Session Won't Start**
- Check OAuth token validity
- Verify Groq API key
- Ensure no other bot is using the same token
- Check system resources

### **Multiple Sessions Conflict**
- Use different OAuth tokens for each session
- Set different wait times between sessions
- Monitor API rate limits
- Check for duplicate project processing

### **Performance Issues**
- Reduce number of concurrent sessions
- Lower bid limits per session
- Increase wait times between operations
- Monitor system memory usage

### **Configuration Issues**
- Verify all required fields are filled
- Check API key formats
- Ensure portfolio links are valid
- Test bid writing style syntax

## API Endpoints

The multi-session system adds these new API endpoints:

- `POST /sessions` - Create new session
- `GET /sessions` - Get all sessions
- `GET /sessions/{id}` - Get specific session
- `PUT /sessions/{id}` - Update session
- `DELETE /sessions/{id}` - Delete session
- `POST /sessions/{id}/start` - Start bot for session
- `POST /sessions/{id}/stop` - Stop bot for session
- `GET /sessions/{id}/status` - Get bot status
- `GET /sessions/status` - Get all bot statuses
- `GET /sessions/{id}/statistics` - Get session statistics

## Migration from Single Session

If you're upgrading from the single-session version:

1. **Your existing configuration** will continue to work
2. **Create a new session** with your current settings
3. **Test the new session** to ensure it works correctly
4. **Gradually migrate** to the multi-session system
5. **Keep the old configuration** as backup initially

## Support

For issues with multi-session functionality:

1. **Check the logs** for error messages
2. **Verify API keys** are correct and active
3. **Test with a single session** first
4. **Check system resources** and performance
5. **Review the configuration** for any issues

The multi-session system is designed to be robust and secure, allowing you to efficiently manage multiple Freelancer accounts while maintaining complete separation and security between them.




