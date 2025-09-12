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
from sqlalchemy import text

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
    retry_count: Optional[int] = None
    retry_wait_seconds: Optional[int] = None
    skill_ids: Optional[List[int]] = None
    language_codes: Optional[List[str]] = None
    unwanted_currencies: Optional[List[str]] = None
    unwanted_countries: Optional[List[str]] = None
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

@app.get("/sessions/persistent-status")
async def get_persistent_bot_status():
    """Get status of persistent bots (bots that survive server restarts)"""
    try:
        # Get all running bot sessions from database
        running_sessions = database_service.get_running_bot_sessions()
        
        persistent_status = []
        for session in running_sessions:
            session_info = {
                "session_id": session.session_id,
                "status": session.status,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "total_bids_placed": session.total_bids_placed,
                "total_projects_found": session.total_projects_found,
                "total_errors": session.total_errors
            }
            persistent_status.append(session_info)
        
        return {
            "persistent_bots": persistent_status,
            "count": len(persistent_status),
            "message": "Bots will automatically resume when server restarts"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get persistent bot status: {str(e)}")

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
            "oauth_token": user_config.get('oauth_token', ''),
            "groq_api_key": user_config.get('groq_api_key', ''),
            "bid_limit": user_config.get('bid_limit', BID_LIMIT),
            "project_search_limit": user_config.get('project_search_limit', PROJECT_SEARCH_LIMIT),
            "min_wait_time": user_config.get('min_wait_time', MIN_WAIT_TIME),
            "retry_count": user_config.get('retry_count', RETRY_COUNT),
            "retry_wait_seconds": user_config.get('retry_wait_seconds', RETRY_WAIT_SECONDS),
            "skill_ids": user_config.get('skill_ids', SKILL_IDS),
            "language_codes": user_config.get('language_codes', LANGUAGE_CODES),
            "unwanted_currencies": user_config.get('unwanted_currencies', list(UNWANTED_CURRENCIES)),
            "unwanted_countries": user_config.get('unwanted_countries', list(UNWANTED_COUNTRIES)),
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
        # Get current config
        user_config = config_manager.get_all_config()
        
        # Update all provided fields
        update_data = {}
        
        # API Keys
        if config_update.oauth_token is not None:
            update_data['oauth_token'] = config_update.oauth_token
        if config_update.groq_api_key is not None:
            update_data['groq_api_key'] = config_update.groq_api_key
            
        # Bot Settings
        if config_update.bid_limit is not None:
            update_data['bid_limit'] = config_update.bid_limit
        if config_update.project_search_limit is not None:
            update_data['project_search_limit'] = config_update.project_search_limit
        if config_update.min_wait_time is not None:
            update_data['min_wait_time'] = config_update.min_wait_time
        if config_update.retry_count is not None:
            update_data['retry_count'] = config_update.retry_count
        if config_update.retry_wait_seconds is not None:
            update_data['retry_wait_seconds'] = config_update.retry_wait_seconds
            
        # Filter Settings
        if config_update.skill_ids is not None:
            update_data['skill_ids'] = config_update.skill_ids
        if config_update.language_codes is not None:
            update_data['language_codes'] = config_update.language_codes
        if config_update.unwanted_currencies is not None:
            update_data['unwanted_currencies'] = config_update.unwanted_currencies
        if config_update.unwanted_countries is not None:
            update_data['unwanted_countries'] = config_update.unwanted_countries
            
        # Bid Configuration
        if config_update.service_offerings is not None:
            update_data['service_offerings'] = config_update.service_offerings
        if config_update.bid_writing_style is not None:
            update_data['bid_writing_style'] = config_update.bid_writing_style
        if config_update.portfolio_links is not None:
            update_data['portfolio_links'] = config_update.portfolio_links
        if config_update.signature is not None:
            update_data['signature'] = config_update.signature
        
        # Save all updates
        if update_data:
            config_manager.update(update_data)
        
        # Get updated configuration
        user_config = config_manager.get_all_config()
        
        updated_config = {
            "oauth_token": user_config.get('oauth_token', ''),
            "groq_api_key": user_config.get('groq_api_key', ''),
            "bid_limit": user_config.get('bid_limit', BID_LIMIT),
            "project_search_limit": user_config.get('project_search_limit', PROJECT_SEARCH_LIMIT),
            "min_wait_time": user_config.get('min_wait_time', MIN_WAIT_TIME),
            "retry_count": user_config.get('retry_count', RETRY_COUNT),
            "retry_wait_seconds": user_config.get('retry_wait_seconds', RETRY_WAIT_SECONDS),
            "skill_ids": user_config.get('skill_ids', SKILL_IDS),
            "language_codes": user_config.get('language_codes', LANGUAGE_CODES),
            "unwanted_currencies": user_config.get('unwanted_currencies', list(UNWANTED_CURRENCIES)),
            "unwanted_countries": user_config.get('unwanted_countries', list(UNWANTED_COUNTRIES)),
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
    """Get analytics overview with session-specific data"""
    try:
        # Get all sessions
        all_sessions = session_manager.get_all_sessions()
        
        # Get all session statuses
        session_statuses = session_manager.get_all_bot_statuses()
        
        # Get database statistics
        stats = database_service.get_bot_statistics()
        
        # Calculate aggregated metrics across all sessions
        total_projects = stats.get('total_projects', 0)
        total_bids = stats.get('total_bids', 0)
        successful_bids = stats.get('successful_bids', 0)
        success_rate = (successful_bids / total_bids * 100) if total_bids > 0 else 0
        
        # Get session-specific statistics
        session_stats = []
        running_sessions = 0
        
        for session in all_sessions:
            try:
                session_id = session['session_id']
                session_status = next((s for s in session_statuses if s.get('session_id') == session_id), None)
                
                if session_status and session_status.get('is_running'):
                    running_sessions += 1
                
                # Get session-specific statistics from database
                session_db_stats = database_service.get_session_statistics(session_id)
                
                session_stats.append({
                    'session_id': session_id,
                    'name': session.get('name', 'Unknown'),
                    'status': session_status.get('status', 'stopped') if session_status else 'stopped',
                    'is_running': session_status.get('is_running', False) if session_status else False,
                    'total_bids': session_db_stats.get('total_bids', 0),
                    'total_projects': session_db_stats.get('total_projects', 0),
                    'successful_bids': session_db_stats.get('successful_bids', 0),
                    'success_rate': session_db_stats.get('success_rate', 0),
                    'start_time': session_status.get('start_time') if session_status else None,
                    'bid_limit': session.get('bid_limit', 0),
                    'bid_counter': session_status.get('bid_counter', 0) if session_status else 0
                })
            except Exception as e:
                print(f"Error processing session {session.get('session_id', 'unknown')}: {e}")
                continue
        
        overview = {
            "total_projects": total_projects,
            "total_bids": total_bids,
            "successful_bids": successful_bids,
            "success_rate": round(success_rate, 2),
            "total_sessions": len(all_sessions),
            "running_sessions": running_sessions,
            "sessions": session_stats,
            "recent_sessions": stats.get('recent_sessions', [])
        }
        
        return overview
    except Exception as e:
        print(f"Analytics overview error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/analytics/performance")
async def get_performance_analytics():
    """Get performance analytics with real data"""
    try:
        db = database_service.get_session()
        try:
            # Get daily bid trends (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            daily_bids = db.execute(text("""
                SELECT DATE(bid_date) as date, COUNT(*) as bids, COUNT(DISTINCT project_id) as projects
                FROM bids 
                WHERE bid_date >= :start_date
                GROUP BY DATE(bid_date)
                ORDER BY date DESC
                LIMIT 30
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Get project type distribution
            project_types = db.execute(text("""
                SELECT project_type, COUNT(*) as count
                FROM projects
                WHERE created_at >= :start_date
                GROUP BY project_type
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Get currency distribution
            currency_dist = db.execute(text("""
                SELECT currency, COUNT(*) as count
                FROM projects
                WHERE created_at >= :start_date AND currency IS NOT NULL
                GROUP BY currency
                ORDER BY count DESC
                LIMIT 10
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Get budget range distribution
            budget_ranges = db.execute(text("""
                SELECT 
                    CASE 
                        WHEN minimum_budget <= 100 THEN 'Under $100'
                        WHEN minimum_budget <= 500 THEN '$100-$500'
                        WHEN minimum_budget <= 1000 THEN '$500-$1K'
                        WHEN minimum_budget <= 5000 THEN '$1K-$5K'
                        ELSE 'Over $5K'
                    END as budget_range,
                    COUNT(*) as count
                FROM projects
                WHERE created_at >= :start_date AND minimum_budget IS NOT NULL
                GROUP BY budget_range
                ORDER BY minimum_budget
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Get session performance
            session_performance = db.execute(text("""
                SELECT 
                    bs.session_id,
                    bs.total_bids_placed,
                    bs.total_projects_found,
                    bs.total_errors,
                    bs.start_time,
                    bs.end_time,
                    bs.status,
                    COUNT(DISTINCT b.project_id) as unique_projects_bid_on
                FROM bot_sessions bs
                LEFT JOIN bids b ON bs.session_id = b.session_id
                WHERE bs.start_time >= :start_date
                GROUP BY bs.session_id
                ORDER BY bs.start_time DESC
                LIMIT 20
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Calculate success rate by hour
            hourly_success = db.execute(text("""
                SELECT 
                    strftime('%H', bid_date) as hour,
                    COUNT(*) as total_bids,
                    SUM(CASE WHEN status = 'placed' THEN 1 ELSE 0 END) as successful_bids
                FROM bids
                WHERE bid_date >= :start_date
                GROUP BY strftime('%H', bid_date)
                ORDER BY hour
            """), {"start_date": thirty_days_ago}).fetchall()
            
            return {
                "daily_trends": [
                    {
                        "date": row[0] if row[0] else None,
                        "bids": row[1],
                        "projects": row[2]
                    } for row in daily_bids
                ],
                "project_types": [
                    {"name": row[0] or "Unknown", "count": row[1]} 
                    for row in project_types
                ],
                "currency_distribution": [
                    {"name": row[0], "count": row[1]} 
                    for row in currency_dist
                ],
                "budget_ranges": [
                    {"name": row[0], "count": row[1]} 
                    for row in budget_ranges
                ],
                "session_performance": [
                    {
                        "session_id": row[0],
                        "total_bids_placed": row[1],
                        "total_projects_found": row[2],
                        "total_errors": row[3],
                        "start_time": row[4].isoformat() if row[4] and hasattr(row[4], 'isoformat') else str(row[4]) if row[4] else None,
                        "end_time": row[5].isoformat() if row[5] and hasattr(row[5], 'isoformat') else str(row[5]) if row[5] else None,
                        "status": row[6],
                        "unique_projects_bid_on": row[7],
                        "efficiency": round((row[7] / max(row[1], 1)) * 100, 2) if row[1] > 0 else 0
                    } for row in session_performance
                ],
                "hourly_success": [
                    {
                        "hour": row[0],
                        "total_bids": row[1],
                        "successful_bids": row[2],
                        "success_rate": round((row[2] / max(row[1], 1)) * 100, 2) if row[1] > 0 else 0
                    } for row in hourly_success
                ]
            }
        finally:
            db.close()
    except Exception as e:
        print(f"Performance analytics error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")

@app.get("/analytics/insights")
async def get_analytics_insights():
    """Get AI-powered insights and recommendations"""
    try:
        db = database_service.get_session()
        try:
            # Get recent performance data
            from datetime import datetime, timedelta
            seven_days_ago = datetime.now() - timedelta(days=7)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Calculate recent vs historical performance
            recent_bids = db.execute(text("""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'placed' THEN 1 ELSE 0 END) as successful,
                       AVG(bid_amount) as avg_bid_amount
                FROM bids 
                WHERE bid_date >= :start_date
            """), {"start_date": seven_days_ago}).fetchone()
            
            historical_bids = db.execute(text("""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'placed' THEN 1 ELSE 0 END) as successful,
                       AVG(bid_amount) as avg_bid_amount
                FROM bids 
                WHERE bid_date >= :start_date AND bid_date < :end_date
            """), {"start_date": thirty_days_ago, "end_date": seven_days_ago}).fetchone()
            
            # Get best performing hours
            best_hours = db.execute(text("""
                SELECT strftime('%H', bid_date) as hour,
                       COUNT(*) as total_bids,
                       SUM(CASE WHEN status = 'placed' THEN 1 ELSE 0 END) as successful_bids,
                       ROUND((SUM(CASE WHEN status = 'placed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate
                FROM bids
                WHERE bid_date >= :start_date
                GROUP BY strftime('%H', bid_date)
                HAVING COUNT(*) >= 3
                ORDER BY success_rate DESC
                LIMIT 5
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Get most successful project types
            successful_projects = db.execute(text("""
                SELECT p.project_type, COUNT(*) as total_bids,
                       SUM(CASE WHEN b.status = 'placed' THEN 1 ELSE 0 END) as successful_bids,
                       ROUND((SUM(CASE WHEN b.status = 'placed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate
                FROM projects p
                JOIN bids b ON p.project_id = b.project_id
                WHERE b.bid_date >= :start_date
                GROUP BY p.project_type
                HAVING COUNT(*) >= 2
                ORDER BY success_rate DESC
                LIMIT 5
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Get optimal budget ranges
            budget_performance = db.execute(text("""
                SELECT 
                    CASE 
                        WHEN p.minimum_budget <= 100 THEN 'Under $100'
                        WHEN p.minimum_budget <= 500 THEN '$100-$500'
                        WHEN p.minimum_budget <= 1000 THEN '$500-$1K'
                        WHEN p.minimum_budget <= 5000 THEN '$1K-$5K'
                        ELSE 'Over $5K'
                    END as budget_range,
                    COUNT(*) as total_bids,
                    SUM(CASE WHEN b.status = 'placed' THEN 1 ELSE 0 END) as successful_bids,
                    ROUND((SUM(CASE WHEN b.status = 'placed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate
                FROM projects p
                JOIN bids b ON p.project_id = b.project_id
                WHERE b.bid_date >= :start_date AND p.minimum_budget IS NOT NULL
                GROUP BY budget_range
                HAVING COUNT(*) >= 2
                ORDER BY success_rate DESC
            """), {"start_date": thirty_days_ago}).fetchall()
            
            # Calculate trends
            recent_success_rate = (recent_bids[1] / max(recent_bids[0], 1)) * 100 if recent_bids[0] > 0 else 0
            historical_success_rate = (historical_bids[1] / max(historical_bids[0], 1)) * 100 if historical_bids[0] > 0 else 0
            success_trend = recent_success_rate - historical_success_rate
            
            insights = []
            recommendations = []
            
            # Generate insights based on data
            if success_trend > 5:
                insights.append({
                    "type": "positive",
                    "title": "Improving Performance",
                    "description": f"Your success rate has improved by {success_trend:.1f}% in the last 7 days compared to the previous period."
                })
            elif success_trend < -5:
                insights.append({
                    "type": "warning",
                    "title": "Performance Decline",
                    "description": f"Your success rate has decreased by {abs(success_trend):.1f}% in the last 7 days. Consider reviewing your bidding strategy."
                })
            
            if best_hours:
                best_hour = best_hours[0]
                insights.append({
                    "type": "info",
                    "title": "Best Performing Hour",
                    "description": f"You have the highest success rate ({best_hour[3]}%) at {best_hour[0]}:00 with {best_hour[1]} total bids."
                })
                recommendations.append({
                    "title": "Optimize Bidding Schedule",
                    "description": f"Consider increasing bid activity around {best_hour[0]}:00 for better results.",
                    "priority": "medium"
                })
            
            if successful_projects:
                best_project_type = successful_projects[0]
                insights.append({
                    "type": "info",
                    "title": "Most Successful Project Type",
                    "description": f"{best_project_type[0]} projects have the highest success rate ({best_project_type[3]}%) with {best_project_type[1]} total bids."
                })
                recommendations.append({
                    "title": "Focus on High-Success Project Types",
                    "description": f"Prioritize bidding on {best_project_type[0]} projects for better success rates.",
                    "priority": "high"
                })
            
            if budget_performance:
                best_budget = budget_performance[0]
                insights.append({
                    "type": "info",
                    "title": "Optimal Budget Range",
                    "description": f"Projects in the {best_budget[0]} range show the highest success rate ({best_budget[3]}%) with {best_budget[1]} total bids."
                })
                recommendations.append({
                    "title": "Target Optimal Budget Ranges",
                    "description": f"Focus on projects in the {best_budget[0]} budget range for better success rates.",
                    "priority": "high"
                })
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "performance_summary": {
                    "recent_success_rate": round(recent_success_rate, 2),
                    "historical_success_rate": round(historical_success_rate, 2),
                    "success_trend": round(success_trend, 2),
                    "recent_total_bids": recent_bids[0],
                    "historical_total_bids": historical_bids[0]
                },
                "best_performing_hours": [
                    {"hour": row[0], "success_rate": row[3], "total_bids": row[1]}
                    for row in best_hours
                ],
                "best_project_types": [
                    {"type": row[0], "success_rate": row[3], "total_bids": row[1]}
                    for row in successful_projects
                ],
                "optimal_budget_ranges": [
                    {"range": row[0], "success_rate": row[3], "total_bids": row[1]}
                    for row in budget_performance
                ]
            }
        finally:
            db.close()
    except Exception as e:
        print(f"Insights analytics error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

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
