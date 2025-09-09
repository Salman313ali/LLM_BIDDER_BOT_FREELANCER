"""
Database service for the Freelancer Bot
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session as DBSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import DATABASE_URL
from .models import Base, Project, Bid, BotSession, BotLog

class DatabaseService:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> DBSession:
        """Get database session"""
        return self.SessionLocal()
    
    def create_bot_session(self, session_id: str, configuration: Dict[str, Any] = None) -> BotSession:
        """Create a new bot session or get existing one"""
        db = self.get_session()
        try:
            # Check if session already exists
            existing_session = db.query(BotSession).filter(BotSession.session_id == session_id).first()
            if existing_session:
                # Update existing session with new configuration
                if configuration:
                    existing_session.configuration = configuration
                    db.commit()
                    db.refresh(existing_session)
                return existing_session
            
            # Create new session
            bot_session = BotSession(
                session_id=session_id,
                configuration=configuration or {}
            )
            db.add(bot_session)
            db.commit()
            db.refresh(bot_session)
            return bot_session
        finally:
            db.close()
    
    def update_bot_session(self, session_id: str, **kwargs) -> bool:
        """Update bot session"""
        db = self.get_session()
        try:
            session = db.query(BotSession).filter(BotSession.session_id == session_id).first()
            if session:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Error updating bot session: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_bot_session(self, session_id: str) -> Optional[BotSession]:
        """Get bot session by ID"""
        db = self.get_session()
        try:
            return db.query(BotSession).filter(BotSession.session_id == session_id).first()
        finally:
            db.close()
    
    def reset_bot_session(self, session_id: str) -> bool:
        """Reset bot session to initial state"""
        db = self.get_session()
        try:
            session = db.query(BotSession).filter(BotSession.session_id == session_id).first()
            if session:
                session.status = 'stopped'
                session.start_time = None
                session.end_time = None
                session.total_projects_found = 0
                session.total_projects_filtered = 0
                session.total_bids_placed = 0
                session.total_errors = 0
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Error resetting bot session: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def log_bot_activity(self, session_id: str, level: str, message: str, 
                        project_id: str = None, additional_data: Dict[str, Any] = None):
        """Log bot activity"""
        db = self.get_session()
        try:
            log_entry = BotLog(
                session_id=session_id,
                level=level,
                message=message,
                project_id=project_id,
                additional_data=additional_data
            )
            db.add(log_entry)
            db.commit()
        except SQLAlchemyError as e:
            print(f"Error logging bot activity: {e}")
            db.rollback()
        finally:
            db.close()
    
    def save_project(self, project_data: Dict[str, Any]) -> Optional[Project]:
        """Save project to database"""
        db = self.get_session()
        try:
            # Check if project already exists
            existing_project = db.query(Project).filter(Project.project_id == project_data['id']).first()
            if existing_project:
                return existing_project
            
            # Convert submitdate from Unix timestamp to datetime if needed
            submitdate = project_data.get('submitdate')
            if submitdate and isinstance(submitdate, (int, float)):
                from datetime import datetime
                submitdate = datetime.fromtimestamp(submitdate)
            
            project = Project(
                project_id=project_data['id'],
                project_title=project_data.get('project_title'),
                project_description=project_data.get('project_description'),
                owner_id=project_data.get('owner_id'),
                minimum_budget=project_data.get('minimum_budget'),
                maximum_budget=project_data.get('maximum_budget'),
                currency=project_data.get('currency'),
                project_type=project_data.get('type'),
                exchange_rate=project_data.get('exchange_rate'),
                submitdate=submitdate,
                seo_url=project_data.get('seo_url')
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            return project
        except SQLAlchemyError as e:
            print(f"Error saving project: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def save_bid(self, bid_data: Dict[str, Any]) -> Optional[Bid]:
        """Save bid to database"""
        db = self.get_session()
        try:
            bid = Bid(
                project_id=bid_data['project_id'],
                bid_amount=bid_data['bid_amount'],
                bid_period=bid_data['bid_period'],
                bid_content=bid_data['bid_content'],
                currency_code=bid_data['currency_code'],
                project_link=bid_data.get('project_link'),
                session_id=bid_data.get('session_id'),
                project_title=bid_data.get('project_title')
            )
            db.add(bid)
            db.commit()
            db.refresh(bid)
            return bid
        except SQLAlchemyError as e:
            print(f"Error saving bid: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def get_recent_bids(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent bids"""
        db = self.get_session()
        try:
            bids = db.query(Bid).order_by(Bid.bid_date.desc()).limit(limit).all()
            return [
                {
                    'id': bid.id,
                    'project_id': bid.project_id,
                    'project_title': bid.project_title,
                    'bid_amount': bid.bid_amount,
                    'bid_period': bid.bid_period,
                    'bid_content': bid.bid_content,
                    'currency_code': bid.currency_code,
                    'status': bid.status,
                    'bid_date': bid.bid_date.isoformat() if bid.bid_date else None,
                    'project_link': bid.project_link,
                    'session_id': bid.session_id
                }
                for bid in bids
            ]
        finally:
            db.close()
    
    def get_bot_statistics(self, session_id: str = None) -> Dict[str, Any]:
        """Get bot statistics"""
        db = self.get_session()
        try:
            # Get session-specific stats if session_id provided
            if session_id:
                session = db.query(BotSession).filter(BotSession.session_id == session_id).first()
                if session:
                    return {
                        'session_id': session.session_id,
                        'start_time': session.start_time.isoformat() if session.start_time else None,
                        'end_time': session.end_time.isoformat() if session.end_time else None,
                        'status': session.status,
                        'total_projects_found': session.total_projects_found,
                        'total_projects_filtered': session.total_projects_filtered,
                        'total_bids_placed': session.total_bids_placed,
                        'total_errors': session.total_errors
                    }
            
            # Get overall stats
            total_projects = db.query(Project).count()
            total_bids = db.query(Bid).count()
            successful_bids = db.query(Bid).filter(Bid.status == 'placed').count()
            
            # Get recent activity
            recent_sessions = db.query(BotSession).order_by(BotSession.start_time.desc()).limit(10).all()
            
            return {
                'total_projects': total_projects,
                'total_bids': total_bids,
                'successful_bids': successful_bids,
                'recent_sessions': [
                    {
                        'session_id': session.session_id,
                        'start_time': session.start_time.isoformat() if session.start_time else None,
                        'status': session.status,
                        'total_bids_placed': session.total_bids_placed
                    }
                    for session in recent_sessions
                ]
            }
        finally:
            db.close()
    
    def log_bid_to_excel(self, bid_data: Dict[str, Any], filename: str = "bid_log.xlsx"):
        """Log bid details to Excel file"""
        try:
            # Prepare row data
            row = {
                "Project ID": bid_data["project_id"],
                "Project Title": bid_data.get("project_title", ""),
                "Project Description": bid_data.get("project_description", ""),
                "Project Budget": bid_data["bid_amount"],
                "Project Timeline": bid_data["bid_period"],
                "Project Link": bid_data.get("project_link", ""),
                "Bid Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Load existing data or create new DataFrame
            if os.path.exists(filename):
                df = pd.read_excel(filename)
                new_row_df = pd.DataFrame([row])
                df = pd.concat([df, new_row_df], ignore_index=True)
            else:
                df = pd.DataFrame([row])
            
            # Save to Excel
            df.to_excel(filename, index=False)
            print(f"Logged bid details to {filename}")
            return True
            
        except Exception as e:
            print(f"Error logging to Excel: {e}")
            return False
    
    def get_project_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get project history"""
        db = self.get_session()
        try:
            projects = db.query(Project).order_by(Project.created_at.desc()).limit(limit).all()
            return [
                {
                    'id': project.id,
                    'project_id': project.project_id,
                    'project_title': project.project_title,
                    'minimum_budget': project.minimum_budget,
                    'maximum_budget': project.maximum_budget,
                    'currency': project.currency,
                    'project_type': project.project_type,
                    'status': project.status,
                    'created_at': project.created_at.isoformat() if project.created_at else None
                }
                for project in projects
            ]
        finally:
            db.close()
