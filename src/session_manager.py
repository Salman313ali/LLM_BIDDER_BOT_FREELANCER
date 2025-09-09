"""
Session Manager for handling multiple bot instances
"""
import uuid
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from .bot import FreelancerBot
from .config_manager import ConfigManager
from .database import DatabaseService

@dataclass
class UserSession:
    """User session configuration"""
    session_id: str
    name: str
    oauth_token: str
    groq_api_key: str
    service_offerings: str
    bid_writing_style: str
    portfolio_links: str
    signature: str
    bid_limit: int = 75
    project_search_limit: int = 10
    min_wait_time: int = 32
    skill_ids: List[int] = None
    language_codes: List[str] = None
    unwanted_currencies: List[str] = None
    unwanted_countries: List[str] = None
    created_at: datetime = None
    is_active: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.skill_ids is None:
            from .config import SKILL_IDS
            self.skill_ids = SKILL_IDS
        if self.language_codes is None:
            from .config import LANGUAGE_CODES
            self.language_codes = LANGUAGE_CODES
        if self.unwanted_currencies is None:
            from .config import UNWANTED_CURRENCIES
            self.unwanted_currencies = list(UNWANTED_CURRENCIES)
        if self.unwanted_countries is None:
            from .config import UNWANTED_COUNTRIES
            self.unwanted_countries = list(UNWANTED_COUNTRIES)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.bot_instances: Dict[str, FreelancerBot] = {}
        self.bot_threads: Dict[str, threading.Thread] = {}
        self.database = DatabaseService()
        self.config_manager = ConfigManager("sessions_config.json")
        self.load_sessions()
    
    def create_session(self, name: str, oauth_token: str, groq_api_key: str,
                      service_offerings: str = "", bid_writing_style: str = "",
                      portfolio_links: str = "", signature: str = "",
                      bid_limit: int = 75, **kwargs) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        
        session = UserSession(
            session_id=session_id,
            name=name,
            oauth_token=oauth_token,
            groq_api_key=groq_api_key,
            service_offerings=service_offerings,
            bid_writing_style=bid_writing_style,
            portfolio_links=portfolio_links,
            signature=signature,
            bid_limit=bid_limit,
            **kwargs
        )
        
        self.sessions[session_id] = session
        self.save_sessions()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions as dictionaries"""
        return [asdict(session) for session in self.sessions.values()]
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session configuration"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        self.save_sessions()
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            # Stop bot if running
            self.stop_bot(session_id)
            del self.sessions[session_id]
            self.save_sessions()
            return True
        return False
    
    def start_bot(self, session_id: str) -> Dict[str, Any]:
        """Start bot for a specific session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        if session_id in self.bot_instances and self.bot_instances[session_id].is_running:
            return {"error": "Bot is already running for this session"}
        
        # Check if there's a running session in the database
        existing_session = self.database.get_bot_session(session_id)
        if existing_session and existing_session.status == 'running':
            # Reset the database session
            self.database.reset_bot_session(session_id)
        
        try:
            # Create bot instance with session-specific configuration
            bot = self._create_bot_for_session(session)
            self.bot_instances[session_id] = bot
            
            # Start bot in a separate thread
            def run_bot():
                bot.start(session.bid_limit)
            
            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()
            self.bot_threads[session_id] = thread
            
            # Mark session as active
            session.is_active = True
            
            return {
                "status": "started",
                "session_id": session_id,
                "session_name": session.name,
                "bot_session_id": bot.session_id
            }
        except Exception as e:
            return {"error": f"Failed to start bot: {str(e)}"}
    
    def stop_bot(self, session_id: str) -> Dict[str, Any]:
        """Stop bot for a specific session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        if session_id not in self.bot_instances:
            return {"error": "Bot is not running for this session"}
        
        try:
            bot = self.bot_instances[session_id]
            result = bot.stop()
            
            # Mark session as inactive
            session.is_active = False
            
            # Clean up
            if session_id in self.bot_threads:
                del self.bot_threads[session_id]
            del self.bot_instances[session_id]
            
            return {
                "status": "stopped",
                "session_id": session_id,
                "session_name": session.name,
                **result
            }
        except Exception as e:
            return {"error": f"Failed to stop bot: {str(e)}"}
    
    def get_bot_status(self, session_id: str) -> Dict[str, Any]:
        """Get bot status for a specific session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        if session_id not in self.bot_instances:
            return {
                "session_id": session_id,
                "session_name": session.name,
                "is_running": False,
                "message": "Bot not running"
            }
        
        try:
            bot = self.bot_instances[session_id]
            status = bot.get_status()
            status.update({
                "session_id": session_id,
                "session_name": session.name
            })
            return status
        except Exception as e:
            return {"error": f"Failed to get bot status: {str(e)}"}
    
    def get_all_bot_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all bots"""
        statuses = []
        for session_id in self.sessions:
            status = self.get_bot_status(session_id)
            statuses.append(status)
        return statuses
    
    def _create_bot_for_session(self, session: UserSession) -> FreelancerBot:
        """Create a bot instance with session-specific configuration"""
        # Create a temporary config manager for this session
        session_config = ConfigManager(f"session_{session.session_id}_config.json")
        
        # Set session-specific configuration
        session_config.update_api_keys(
            oauth_token=session.oauth_token,
            groq_api_key=session.groq_api_key
        )
        
        session_config.update_bid_config(
            service_offerings=session.service_offerings,
            bid_writing_style=session.bid_writing_style,
            portfolio_links=session.portfolio_links,
            signature=session.signature
        )
        
        # Create bot instance with session-specific parameters
        bot = FreelancerBot(
            session_id=session.session_id,
            bid_limit=session.bid_limit,
            project_search_limit=session.project_search_limit,
            min_wait_time=session.min_wait_time,
            skill_ids=session.skill_ids,
            language_codes=session.language_codes,
            unwanted_currencies=session.unwanted_currencies,
            unwanted_countries=session.unwanted_countries,
            config_manager_instance=session_config
        )
        
        # Override the global config manager for this bot instance
        bot.freelancer_service.config_manager = session_config
        
        # Update the FreelancerService session with the session-specific OAuth token
        from freelancersdk.session import Session
        bot.freelancer_service.session = Session(oauth_token=session.oauth_token)
        
        return bot
    
    def save_sessions(self):
        """Save sessions to file"""
        sessions_data = {}
        for session_id, session in self.sessions.items():
            sessions_data[session_id] = asdict(session)
            # Convert datetime to string for JSON serialization
            if sessions_data[session_id]['created_at']:
                sessions_data[session_id]['created_at'] = sessions_data[session_id]['created_at'].isoformat()
        
        self.config_manager.save_config(sessions_data)
    
    def load_sessions(self):
        """Load sessions from file"""
        sessions_data = self.config_manager.get_all_config()
        
        for session_id, data in sessions_data.items():
            # Convert string back to datetime
            if data.get('created_at'):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            
            session = UserSession(**data)
            self.sessions[session_id] = session
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a specific session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        try:
            if session_id in self.bot_instances:
                bot = self.bot_instances[session_id]
                return bot.get_statistics()
            else:
                return self.database.get_bot_statistics()
        except Exception as e:
            return {"error": f"Failed to get statistics: {str(e)}"}

# Global session manager instance
session_manager = SessionManager()
