"""
Configuration Manager for dynamic configuration updates
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file: str = "user_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                return {}
        return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def get_oauth_token(self) -> Optional[str]:
        """Get OAuth token"""
        return self.get('oauth_token')
    
    def get_groq_api_key(self) -> Optional[str]:
        """Get Groq API key"""
        return self.get('groq_api_key')
    
    def get_service_offerings(self) -> str:
        """Get service offerings"""
        return self.get('service_offerings', '')
    
    def get_bid_writing_style(self) -> str:
        """Get bid writing style"""
        return self.get('bid_writing_style', '')
    
    def get_portfolio_links(self) -> str:
        """Get portfolio links"""
        return self.get('portfolio_links', '')
    
    def get_signature(self) -> str:
        """Get signature"""
        return self.get('signature', '')
    
    def update_api_keys(self, oauth_token: str = None, groq_api_key: str = None) -> None:
        """Update API keys"""
        if oauth_token:
            self.set('oauth_token', oauth_token)
        if groq_api_key:
            self.set('groq_api_key', groq_api_key)
        self.save_config(self.config)
    
    def update_bid_config(self, service_offerings: str = None, bid_writing_style: str = None, 
                         portfolio_links: str = None, signature: str = None) -> None:
        """Update bid configuration"""
        if service_offerings is not None:
            self.set('service_offerings', service_offerings)
        if bid_writing_style is not None:
            self.set('bid_writing_style', bid_writing_style)
        if portfolio_links is not None:
            self.set('portfolio_links', portfolio_links)
        if signature is not None:
            self.set('signature', signature)
        self.save_config(self.config)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = {}
        self.save_config(self.config)

# Global config manager instance
config_manager = ConfigManager()



