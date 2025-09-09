"""
Main Freelancer Bot class
"""
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import BID_LIMIT, PROJECT_SEARCH_LIMIT
from .freelancer_service import FreelancerService
from .ai_service import AIService
from .database import DatabaseService
from .utils import extract_budget_and_deadline, calculate_bid_amount, validate_project_data

class FreelancerBot:
    def __init__(self, session_id: str = None, bid_limit: int = None, 
                 project_search_limit: int = None, min_wait_time: int = None,
                 skill_ids: List[int] = None, language_codes: List[str] = None,
                 unwanted_currencies: List[str] = None, unwanted_countries: List[str] = None,
                 config_manager_instance=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.processed_project_ids = set()
        self.bid_counter = 0
        self.is_running = False
        
        # Use session-specific parameters or fall back to defaults
        self.bid_limit = bid_limit or BID_LIMIT
        self.project_search_limit = project_search_limit or PROJECT_SEARCH_LIMIT
        self.min_wait_time = min_wait_time or 32
        
        # Set session-specific filtering parameters
        if skill_ids:
            self.skill_ids = skill_ids
        else:
            from .config import SKILL_IDS
            self.skill_ids = SKILL_IDS
            
        if language_codes:
            self.language_codes = language_codes
        else:
            from .config import LANGUAGE_CODES
            self.language_codes = LANGUAGE_CODES
            
        if unwanted_currencies:
            self.unwanted_currencies = unwanted_currencies
        else:
            from .config import UNWANTED_CURRENCIES
            self.unwanted_currencies = list(UNWANTED_CURRENCIES)
            
        if unwanted_countries:
            self.unwanted_countries = unwanted_countries
        else:
            from .config import UNWANTED_COUNTRIES
            self.unwanted_countries = list(UNWANTED_COUNTRIES)
        
        # Create services with session-specific parameters
        self.freelancer_service = FreelancerService(
            skill_ids=self.skill_ids,
            language_codes=self.language_codes,
            unwanted_currencies=self.unwanted_currencies,
            unwanted_countries=self.unwanted_countries
        )
        self.ai_service = AIService(config_manager_instance=config_manager_instance)
        self.database = DatabaseService()
        
        # Create or get existing bot session
        self.bot_session = self.database.create_bot_session(
            self.session_id,
            {
                'bid_limit': self.bid_limit,
                'project_search_limit': self.project_search_limit
            }
        )
        
        # Reset session if it was previously running
        if self.bot_session and self.bot_session.status == 'running':
            self.database.reset_bot_session(self.session_id)
            self.bot_session = self.database.get_bot_session(self.session_id)
    
    def start(self, bid_limit: int = None) -> Dict[str, Any]:
        """
        Start the bot with specified bid limit.
        """
        if self.is_running:
            return {"error": "Bot is already running"}
        
        self.is_running = True
        self.bid_counter = 0
        self.processed_project_ids.clear()
        
        # Update bid limit if provided
        if bid_limit:
            self.bid_limit = bid_limit
        
        # Update session status
        self.database.update_bot_session(
            self.session_id,
            status="running",
            start_time=datetime.now()
        )
        
        self.database.log_bot_activity(
            self.session_id,
            "INFO",
            f"Bot started with bid limit: {self.bid_limit}"
        )
        
        try:
            return self._run_bot_loop()
        except Exception as e:
            self.database.log_bot_activity(
                self.session_id,
                "ERROR",
                f"Bot error: {str(e)}"
            )
            return {"error": str(e)}
        finally:
            self.stop()
    
    def stop(self) -> Dict[str, Any]:
        """
        Stop the bot.
        """
        self.is_running = False
        
        # Update session status
        self.database.update_bot_session(
            self.session_id,
            status="stopped",
            end_time=datetime.now()
        )
        
        self.database.log_bot_activity(
            self.session_id,
            "INFO",
            f"Bot stopped. Total bids placed: {self.bid_counter}"
        )
        
        return {
            "status": "stopped",
            "total_bids_placed": self.bid_counter,
            "session_id": self.session_id
        }
    
    def _run_bot_loop(self) -> Dict[str, Any]:
        """
        Main bot execution loop.
        """
        offset = 0
        
        while self.bid_counter < self.bid_limit and self.is_running:
            try:
                # Search for projects
                projects = self.freelancer_service.search_projects(
                    limit=self.project_search_limit, 
                    offset=offset
                )
                
                if not projects:
                    self.database.log_bot_activity(
                        self.session_id,
                        "WARNING",
                        "No projects found"
                    )
                    time.sleep(5)
                    continue
                
                self.database.log_bot_activity(
                    self.session_id,
                    "INFO",
                    f"Fetched {len(projects)} projects"
                )
                
                # Update session stats
                self.database.update_bot_session(
                    self.session_id,
                    total_projects_found=self.bot_session.total_projects_found + len(projects)
                )
                
                # Filter out already processed projects
                new_projects = [
                    p for p in projects 
                    if p.get('id') not in self.processed_project_ids
                ]
                
                for p in new_projects:
                    self.processed_project_ids.add(p.get('id'))
                
                self.database.log_bot_activity(
                    self.session_id,
                    "INFO",
                    f"{len(new_projects)} new projects after filtering processed ones"
                )
                
                if not new_projects:
                    time.sleep(5)
                    continue
                
                # Filter projects
                filtered_projects = self.freelancer_service.filter_projects(new_projects)
                
                self.database.log_bot_activity(
                    self.session_id,
                    "INFO",
                    f"Filtered down to {len(filtered_projects)} projects"
                )
                
                # Update session stats
                self.database.update_bot_session(
                    self.session_id,
                    total_projects_filtered=self.bot_session.total_projects_filtered + len(filtered_projects)
                )
                
                if not filtered_projects:
                    time.sleep(5)
                    continue
                
                # Refine projects with AI
                refined_projects = self._refine_projects_with_ai(filtered_projects)
                
                self.database.log_bot_activity(
                    self.session_id,
                    "INFO",
                    f"AI refined down to {len(refined_projects)} projects"
                )
                
                if not refined_projects:
                    time.sleep(5)
                    continue
                
                # Generate and place bids
                self._process_bids(refined_projects)
                
                if self.bid_counter >= self.bid_limit:
                    self.database.log_bot_activity(
                        self.session_id,
                        "INFO",
                        "Bid limit reached. Stopping execution."
                    )
                    break
                
                time.sleep(5)
                
            except Exception as e:
                self.database.log_bot_activity(
                    self.session_id,
                    "ERROR",
                    f"Error in bot loop: {str(e)}"
                )
                self.database.update_bot_session(
                    self.session_id,
                    total_errors=self.bot_session.total_errors + 1
                )
                time.sleep(5)
        
        return {
            "status": "completed",
            "total_bids_placed": self.bid_counter,
            "session_id": self.session_id
        }
    
    def _refine_projects_with_ai(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refine projects using AI analysis.
        """
        refined = []
        
        for project in projects:
            try:
                # Validate project data
                if not validate_project_data(project):
                    continue
                
                # Check if project matches our services
                result = self.ai_service.check_project_match(project)
                
                if result.lower() == "match":
                    refined.append(project)
                    self.database.log_bot_activity(
                        self.session_id,
                        "INFO",
                        f"Project {project.get('id')} matched our services",
                        project_id=project.get('id')
                    )
                else:
                    self.database.log_bot_activity(
                        self.session_id,
                        "INFO",
                        f"Project {project.get('id')} did not match our services",
                        project_id=project.get('id')
                    )
                    
            except Exception as e:
                self.database.log_bot_activity(
                    self.session_id,
                    "ERROR",
                    f"AI evaluation failed for project {project.get('id')}: {str(e)}",
                    project_id=project.get('id')
                )
        
        return refined
    
    def _process_bids(self, projects: List[Dict[str, Any]]) -> None:
        """
        Process projects and place bids.
        """
        for project in projects:
            if not self.is_running or self.bid_counter >= self.bid_limit:
                break
            
            try:
                # Save project to database
                self.database.save_project(project)
                
                # Generate bid content
                bid_content = self.ai_service.generate_bid_content(project)
                if not bid_content:
                    continue
                
                # Analyze budget and deadline
                budget_deadline_info = self.ai_service.analyze_budget_deadline(project)
                budget, deadline = extract_budget_and_deadline(budget_deadline_info)
                
                # Calculate bid amount
                bid_amount = calculate_bid_amount(project, budget)
                
                # Set default deadline if not provided
                if deadline is None:
                    deadline = 7 if project.get('type', '').lower() == 'fixed' else 40
                
                # Compose final bid
                final_bid_content = self.ai_service.compose_bid_template(bid_content)
                
                # Prepare bid data
                bid_data = {
                    "project_id": project["id"],
                    "project_title": project["project_title"],
                    "project_description": project["project_description"],
                    "bid_content": final_bid_content,
                    "bid_amount": bid_amount,
                    "bid_period": deadline,
                    "currency_code": project["currency"],
                    "project_link": f"https://www.freelancer.com/projects/{project.get('seo_url', project['id'])}/details",
                    "session_id": self.session_id
                }
                
                # Place bid
                success = self.freelancer_service.process_project_bid(
                    project, final_bid_content, bid_amount, deadline
                )
                
                if success:
                    self.bid_counter += 1
                    
                    # Save bid to database
                    self.database.save_bid(bid_data)
                    
                    # Log to Excel
                    self.database.log_bid_to_excel(bid_data)
                    
                    # Update session stats
                    self.database.update_bot_session(
                        self.session_id,
                        total_bids_placed=self.bid_counter
                    )
                    
                    self.database.log_bot_activity(
                        self.session_id,
                        "INFO",
                        f"Successfully placed bid on project {project['id']}",
                        project_id=project['id'],
                        additional_data={"bid_amount": bid_amount, "bid_period": deadline}
                    )
                else:
                    self.database.log_bot_activity(
                        self.session_id,
                        "ERROR",
                        f"Failed to place bid on project {project['id']}",
                        project_id=project['id']
                    )
                
            except Exception as e:
                self.database.log_bot_activity(
                    self.session_id,
                    "ERROR",
                    f"Error processing bid for project {project.get('id')}: {str(e)}",
                    project_id=project.get('id')
                )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status.
        """
        return {
            "is_running": self.is_running,
            "bid_counter": self.bid_counter,
            "session_id": self.session_id,
            "processed_projects": len(self.processed_project_ids)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get bot statistics.
        """
        return self.database.get_bot_statistics(self.session_id)

