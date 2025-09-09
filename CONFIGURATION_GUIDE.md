# 🔧 Configuration Guide

## Overview

The Freelancer Bot now supports dynamic configuration through the dashboard! You can customize:

- **API Keys**: Your Freelancer.com OAuth token and Groq API key
- **Service Offerings**: What services your bot should look for
- **Bid Writing Style**: How your bids should be written
- **Portfolio Links**: Your portfolio links to include in bids
- **Signature**: Your name/signature for bids

## How to Configure

### 1. Using the Dashboard (Recommended)

1. **Start the dashboard** (backend + frontend)
2. **Go to Configuration tab**
3. **Fill in your details**:
   - **API Configuration**: Enter your OAuth token and Groq API key
   - **Bid Writing Configuration**: Customize your service offerings, bid style, portfolio links, and signature
4. **Click "Save Configuration"**
5. **Restart the bot** to apply changes

### 2. Using Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
FREELANCER_OAUTH_TOKEN=your_oauth_token_here
GROQ_API_KEY=your_groq_api_key_here

# Bid Configuration
SERVICE_OFFERINGS=Your custom service offerings description...
BID_WRITING_STYLE=Your custom bid writing style...
PORTFOLIO_LINKS=Your portfolio links (one per line)
SIGNATURE=Your Name
```

### 3. Using Configuration File

The bot automatically creates a `user_config.json` file when you save settings through the dashboard. You can also manually edit this file:

```json
{
  "oauth_token": "your_oauth_token",
  "groq_api_key": "your_groq_api_key",
  "service_offerings": "Your custom service offerings...",
  "bid_writing_style": "Your custom bid writing style...",
  "portfolio_links": "Your portfolio links...",
  "signature": "Your Name"
}
```

## Configuration Examples

### Example 1: Web Developer

**Service Offerings:**
```
1. Website Development:
   - WordPress development and customization
   - E-commerce websites (WooCommerce, Shopify)
   - React.js applications
   - Responsive web design
   - SEO optimization

2. Web Services:
   - Website maintenance and updates
   - Performance optimization
   - Security implementation
   - Database design and management
```

**Bid Writing Style:**
```
Write a professional freelance proposal for web development projects. 

Structure:
1. Start with a strong opening that shows understanding of the client's needs
2. Highlight relevant experience with specific technologies mentioned
3. Ask 2-3 relevant questions about the project
4. Include portfolio links
5. End with signature

Tone: Professional, confident, and solution-focused. Keep it under 100 words.
```

**Portfolio Links:**
```
https://yourportfolio.com/wordpress-projects
https://yourportfolio.com/ecommerce-sites
https://yourportfolio.com/react-applications
```

**Signature:**
```
Best regards,
John Smith
```

### Example 2: Graphic Designer

**Service Offerings:**
```
1. Graphic Design:
   - Logo design and branding
   - Business card and stationery design
   - Social media graphics
   - Print materials (brochures, flyers, banners)
   - UI/UX design

2. Digital Art:
   - Vector illustrations
   - Digital paintings
   - Icon design
   - Infographic design
```

**Bid Writing Style:**
```
Create a creative and engaging proposal for design projects.

Approach:
- Show enthusiasm for the project
- Demonstrate understanding of design principles
- Ask about brand guidelines and preferences
- Mention turnaround time
- Include relevant portfolio examples

Style: Creative, enthusiastic, and detail-oriented. Keep it conversational and under 80 words.
```

**Portfolio Links:**
```
https://behance.net/yourportfolio
https://dribbble.com/yourwork
https://yourwebsite.com/portfolio
```

**Signature:**
```
Looking forward to working with you!
Sarah Johnson
```

## Tips for Better Configuration

### Service Offerings
- Be specific about what you do and don't do
- Include technologies, tools, and platforms you work with
- Mention any specializations or niches
- Be clear about project types you prefer

### Bid Writing Style
- Define the tone (professional, friendly, creative, etc.)
- Specify word count limits
- Include structure guidelines
- Mention any specific requirements (questions to ask, portfolio inclusion, etc.)

### Portfolio Links
- Use one link per line
- Include diverse examples of your work
- Make sure links are working and up-to-date
- Consider using different platforms (Behance, Dribbble, personal website, etc.)

### Signature
- Keep it professional but personal
- Include your name
- Consider adding a tagline if relevant
- Keep it concise

## Security Notes

- **Never share your API keys** with others
- **Use environment variables** for production deployments
- **Regularly rotate your API keys** for security
- **Keep your configuration file secure** and don't commit it to version control

## Troubleshooting

### Configuration Not Saving
- Check that the backend is running
- Verify you have write permissions in the project directory
- Check the browser console for errors

### Bot Not Using New Configuration
- Restart the bot after saving configuration
- Check that the configuration was saved correctly
- Verify the bot is reading from the correct configuration source

### API Keys Not Working
- Verify the keys are correct and active
- Check that you have the necessary permissions
- Ensure the keys are not expired

## Advanced Configuration

For advanced users, you can also modify the configuration directly in the code:

1. **Edit `src/config.py`** for default values
2. **Modify `src/config_manager.py`** for configuration management logic
3. **Update the AI service** in `src/ai_service.py` for custom prompts

Remember to restart the bot after making code changes!




