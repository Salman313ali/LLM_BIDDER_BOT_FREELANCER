"""
FastAPI backend for Freelancer Bot Dashboard
"""
import asyncio
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.bot import FreelancerBot
from src.database import DatabaseService
from src.models import BotLog
from src.config import *
from src.config_manager import config_manager
from src.session_manager import session_manager, UserSession

# Initialize FastAPI app
app = FastAPI(
    title="Freelancer Bot API",
    description="API for managing and monitoring the Freelancer.com bidding bot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global bot instance (for backward compatibility)
bot_instance: Optional[FreelancerBot] = None
bot_thread: Optional[threading.Thread] = None
database_service = DatabaseService()

# Pydantic models
class BotStartRequest(BaseModel):
    bid_limit: Optional[int] = BID_LIMIT

class BotConfigUpdate(BaseModel):
    oauth_token: Optional[str] = None
    groq_api_key: Optional[str] = None
    bid_limit: Optional[int] = None
    project_search_limit: Optional[int] = None
    min_wait_time: Optional[int] = None
    service_offerings: Optional[str] = None
    bid_writing_style: Optional[str] = None
    portfolio_links: Optional[str] = None
    signature: Optional[str] = None

class ProjectFilter(BaseModel):
    skill_ids: Optional[List[int]] = None
    language_codes: Optional[List[str]] = None
    unwanted_currencies: Optional[List[str]] = None
    unwanted_countries: Optional[List[str]] = None

class SessionCreateRequest(BaseModel):
    name: str
    oauth_token: str
    groq_api_key: str
    service_offerings: Optional[str] = ""
    bid_writing_style: Optional[str] = ""
    portfolio_links: Optional[str] = ""
    signature: Optional[str] = ""
    bid_limit: Optional[int] = 75
    project_search_limit: Optional[int] = 10
    min_wait_time: Optional[int] = 32
    skill_ids: Optional[List[int]] = None
    language_codes: Optional[List[str]] = None
    unwanted_currencies: Optional[List[str]] = None
    unwanted_countries: Optional[List[str]] = None

class SessionUpdateRequest(BaseModel):
    name: Optional[str] = None
    oauth_token: Optional[str] = None
    groq_api_key: Optional[str] = None
    service_offerings: Optional[str] = None
    bid_writing_style: Optional[str] = None
    portfolio_links: Optional[str] = None
    signature: Optional[str] = None
    bid_limit: Optional[int] = None
    project_search_limit: Optional[int] = None
    min_wait_time: Optional[int] = None
    skill_ids: Optional[List[int]] = None
    language_codes: Optional[List[str]] = None
    unwanted_currencies: Optional[List[str]] = None
    unwanted_countries: Optional[List[str]] = None

# Session Management Endpoints
@app.post("/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new user session"""
    try:
        session_id = session_manager.create_session(
            name=request.name,
            oauth_token=request.oauth_token,
            groq_api_key=request.groq_api_key,
            service_offerings=request.service_offerings,
            bid_writing_style=request.bid_writing_style,
            portfolio_links=request.portfolio_links,
            signature=request.signature,
            bid_limit=request.bid_limit,
            project_search_limit=request.project_search_limit,
            min_wait_time=request.min_wait_time,
            skill_ids=request.skill_ids,
            language_codes=request.language_codes,
            unwanted_currencies=request.unwanted_currencies,
            unwanted_countries=request.unwanted_countries
        )
        return {"session_id": session_id, "message": "Session created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/sessions")
async def get_all_sessions():
    """Get all user sessions"""
    try:
        sessions = session_manager.get_all_sessions()
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific session details"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session.__dict__
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.put("/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdateRequest):
    """Update session configuration"""
    try:
        # Convert request to dict, excluding None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        success = session_manager.update_session(session_id, **updates)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.post("/sessions/{session_id}/start")
async def start_session_bot(session_id: str):
    """Start bot for a specific session"""
    try:
        result = session_manager.start_bot(session_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@app.post("/sessions/{session_id}/stop")
async def stop_session_bot(session_id: str):
    """Stop bot for a specific session"""
    try:
        result = session_manager.stop_bot(session_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")

@app.get("/sessions/{session_id}/status")
async def get_session_bot_status(session_id: str):
    """Get bot status for a specific session"""
    try:
        result = session_manager.get_bot_status(session_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bot status: {str(e)}")

@app.get("/sessions/status")
async def get_all_session_statuses():
    """Get status of all session bots"""
    try:
        statuses = session_manager.get_all_bot_statuses()
        return {"statuses": statuses, "count": len(statuses)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bot statuses: {str(e)}")

@app.get("/sessions/{session_id}/statistics")
async def get_session_statistics(session_id: str):
    """Get statistics for a specific session"""
    try:
        result = session_manager.get_session_statistics(session_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Bot Management Endpoints (Legacy - for backward compatibility)
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Freelancer Bot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/bot/start")
async def start_bot(request: BotStartRequest, background_tasks: BackgroundTasks):
    """Start the bot"""
    global bot_instance, bot_thread
    
    if bot_instance and bot_instance.is_running:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    try:
        bot_instance = FreelancerBot()
        
        def run_bot():
            bot_instance.start(request.bid_limit)
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        return {
            "status": "started",
            "session_id": bot_instance.session_id,
            "bid_limit": request.bid_limit or BID_LIMIT,
            "message": "Bot started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@app.post("/bot/stop")
async def stop_bot():
    """Stop the bot"""
    global bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    try:
        result = bot_instance.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")

@app.get("/bot/status")
async def get_bot_status():
    """Get current bot status"""
    global bot_instance
    
    if not bot_instance:
        return {
            "is_running": False,
            "message": "Bot not initialized"
        }
    
    try:
        status = bot_instance.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bot status: {str(e)}")

@app.get("/bot/statistics")
async def get_bot_statistics():
    """Get bot statistics"""
    global bot_instance
    
    try:
        if bot_instance:
            stats = bot_instance.get_statistics()
        else:
            stats = database_service.get_bot_statistics()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Project Management Endpoints
@app.get("/projects")
async def get_projects(limit: int = 100):
    """Get project history"""
    try:
        projects = database_service.get_project_history(limit)
        return {"projects": projects, "count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get specific project details"""
    try:
        # This would need to be implemented in database service
        raise HTTPException(status_code=501, detail="Not implemented yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

# Bid Management Endpoints
@app.get("/bids")
async def get_bids(limit: int = 50):
    """Get recent bids"""
    try:
        bids = database_service.get_recent_bids(limit)
        return {"bids": bids, "count": len(bids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bids: {str(e)}")

@app.get("/bids/{bid_id}")
async def get_bid(bid_id: int):
    """Get specific bid details"""
    try:
        # This would need to be implemented in database service
        raise HTTPException(status_code=501, detail="Not implemented yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bid: {str(e)}")

# Configuration Endpoints
@app.get("/config")
async def get_config():
    """Get current configuration"""
    try:
        # Get user configuration from config manager
        user_config = config_manager.get_all_config()
        
        config = {
            "oauth_token": user_config.get('oauth_token', OAUTH_TOKEN),
            "groq_api_key": user_config.get('groq_api_key', GROQ_API_KEY),
            "bid_limit": BID_LIMIT,
            "project_search_limit": PROJECT_SEARCH_LIMIT,
            "min_wait_time": MIN_WAIT_TIME,
            "retry_count": RETRY_COUNT,
            "retry_wait_seconds": RETRY_WAIT_SECONDS,
            "skill_ids": SKILL_IDS,
            "language_codes": LANGUAGE_CODES,
            "unwanted_currencies": list(UNWANTED_CURRENCIES),
            "unwanted_countries": list(UNWANTED_COUNTRIES),
            "service_offerings": user_config.get('service_offerings', SERVICE_OFFERINGS),
            "bid_writing_style": user_config.get('bid_writing_style', BID_WRITING_STYLE),
            "portfolio_links": user_config.get('portfolio_links', PORTFOLIO_LINKS_TEXT),
            "signature": user_config.get('signature', SIGNATURE)
        }
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@app.put("/config")
async def update_config(config_update: BotConfigUpdate):
    """Update bot configuration"""
    try:
        # Update API keys if provided
        if config_update.oauth_token or config_update.groq_api_key:
            config_manager.update_api_keys(
                oauth_token=config_update.oauth_token,
                groq_api_key=config_update.groq_api_key
            )
        
        # Update bid configuration if provided
        if any([config_update.service_offerings, config_update.bid_writing_style, 
                config_update.portfolio_links, config_update.signature]):
            config_manager.update_bid_config(
                service_offerings=config_update.service_offerings,
                bid_writing_style=config_update.bid_writing_style,
                portfolio_links=config_update.portfolio_links,
                signature=config_update.signature
            )
        
        # Get updated configuration
        user_config = config_manager.get_all_config()
        
        updated_config = {
            "oauth_token": user_config.get('oauth_token', OAUTH_TOKEN),
            "groq_api_key": user_config.get('groq_api_key', GROQ_API_KEY),
            "bid_limit": config_update.bid_limit or BID_LIMIT,
            "project_search_limit": config_update.project_search_limit or PROJECT_SEARCH_LIMIT,
            "min_wait_time": config_update.min_wait_time or MIN_WAIT_TIME,
            "service_offerings": user_config.get('service_offerings', SERVICE_OFFERINGS),
            "bid_writing_style": user_config.get('bid_writing_style', BID_WRITING_STYLE),
            "portfolio_links": user_config.get('portfolio_links', PORTFOLIO_LINKS_TEXT),
            "signature": user_config.get('signature', SIGNATURE),
            "message": "Configuration updated successfully! Restart bot to apply changes."
        }
        return updated_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

# Logging Endpoints
@app.get("/logs")
async def get_logs(session_id: Optional[str] = None, limit: int = 100):
    """Get bot logs"""
    try:
        # Get logs from database
        db = database_service.get_session()
        try:
            query = db.query(BotLog)
            if session_id and session_id != 'null':
                query = query.filter(BotLog.session_id == session_id)
            
            logs = query.order_by(BotLog.timestamp.desc()).limit(limit).all()
            
            log_data = [
                {
                    'id': log.id,
                    'session_id': log.session_id,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                    'level': log.level,
                    'message': log.message,
                    'project_id': log.project_id,
                    'additional_data': log.additional_data
                }
                for log in logs
            ]
            
            return {"logs": log_data, "count": len(log_data)}
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

# Analytics Endpoints
@app.get("/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        stats = database_service.get_bot_statistics()
        
        # Calculate additional metrics
        total_projects = stats.get('total_projects', 0)
        total_bids = stats.get('total_bids', 0)
        successful_bids = stats.get('successful_bids', 0)
        
        success_rate = (successful_bids / total_bids * 100) if total_bids > 0 else 0
        
        overview = {
            "total_projects": total_projects,
            "total_bids": total_bids,
            "successful_bids": successful_bids,
            "success_rate": round(success_rate, 2),
            "recent_sessions": stats.get('recent_sessions', [])
        }
        
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/analytics/performance")
async def get_performance_analytics():
    """Get performance analytics"""
    try:
        # This would need to be implemented with more detailed analytics
        raise HTTPException(status_code=501, detail="Not implemented yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
