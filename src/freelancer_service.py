"""
Freelancer.com API service for project management and bidding
"""
import time
from typing import List, Dict, Any, Optional
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects, get_projects, get_bids
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
    create_get_projects_object,
    create_get_projects_project_details_object,
    create_get_projects_user_details_object
)
from freelancersdk.resources.projects import place_project_bid
from freelancersdk.resources.users import get_self_user_id, get_user_by_id

from .config import OAUTH_TOKEN, SKILL_IDS, LANGUAGE_CODES, UNWANTED_CURRENCIES, UNWANTED_COUNTRIES
from .config_manager import config_manager
from .utils import retry_on_failure, wait_until_20_sec, generate_project_link

class FreelancerService:
    def __init__(self, skill_ids: List[int] = None, language_codes: List[str] = None,
                 unwanted_currencies: List[str] = None, unwanted_countries: List[str] = None):
        # Use configurable OAuth token or fallback to default
        oauth_token = config_manager.get_oauth_token() or OAUTH_TOKEN
        self.session = Session(oauth_token=oauth_token)
        self.projects_endpoint = 'api/projects/0.1'
        self._search_filter = None
        
        # Set session-specific filtering parameters
        self.skill_ids = skill_ids or SKILL_IDS
        self.language_codes = language_codes or LANGUAGE_CODES
        self.unwanted_currencies = unwanted_currencies or list(UNWANTED_CURRENCIES)
        self.unwanted_countries = unwanted_countries or list(UNWANTED_COUNTRIES)
    
    @property
    def search_filter(self):
        """Get or create search filter"""
        if self._search_filter is None:
            self._search_filter = create_search_projects_filter(
                jobs=self.skill_ids,
                languages=self.language_codes,
                sort_field='time_updated',
                or_search_query=True
            )
        return self._search_filter
    
    def get_self_user_id(self) -> Optional[str]:
        """Get current user ID"""
        try:
            return get_self_user_id(self.session)
        except Exception as e:
            print(f"Error getting self user ID: {e}")
            return None
    
    def search_projects(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search for projects using the configured filter.
        """
        try:
            response = search_projects(
                self.session, 
                query='', 
                search_filter=self.search_filter,
                limit=limit, 
                offset=offset
            )
            return response.get('projects', [])
        except Exception as e:
            print(f"Error searching projects: {e}")
            return []
    
    def already_bid_on_project(self, project_id: str, my_user_id: str) -> bool:
        """
        Check if we have already bid on a project.
        """
        try:
            bids = get_bids(self.session, project_id)
            # Handle case where bids might be a string or other format
            if isinstance(bids, str):
                return False
            
            # Ensure bids is iterable
            if not hasattr(bids, '__iter__'):
                return False
                
            for bid in bids:
                # Handle case where bid might be a string
                if isinstance(bid, str):
                    continue
                    
                if hasattr(bid, 'get') and bid.get("bidder_id") == my_user_id:
                    return True
            return False
        except Exception as e:
            print(f"Error checking bids for project {project_id}: {e}")
            return False
    
    def filter_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter projects based on various criteria.
        """
        filtered_projects = []
        my_user_id = self.get_self_user_id()
        
        for project in projects:
            project_id = project.get('id')
            user_id = project.get("owner_id")
            
            if not user_id or not project_id:
                continue
            
            # Check if already bid on this project
            if my_user_id and self.already_bid_on_project(project_id, my_user_id):
                continue
            
            # Check user location
            try:
                user_details = get_user_by_id(self.session, user_id)
                country_name = user_details.get("location", {}).get("country", {}).get("name", "").lower()
                if country_name in self.unwanted_countries:
                    continue
            except Exception as e:
                print(f"Error getting user details for {user_id}: {e}")
                continue
            
            # Check currency
            currency_code = project.get('currency', {}).get('code', '')
            if currency_code in self.unwanted_currencies:
                continue
            
            # Check for NDA requirement
            if project.get('upgrades', {}).get('NDA', False):
                continue
            
            # Check project status
            if project.get('status', '').lower() != 'active':
                continue
            
            # Get complete project details
            try:
                details_obj = create_get_projects_object(
                    project_ids=[project_id],
                    project_details=create_get_projects_project_details_object(
                        full_description=True,
                        jobs=True,
                        qualifications=True,
                        location=True,
                    ),
                    user_details=create_get_projects_user_details_object(
                        basic=True,
                        reputation=True,
                        location=True
                    ),
                )
                complete_details = get_projects(self.session, details_obj)
                
                if len(complete_details['projects']) == 0:
                    continue
                
                project_data = complete_details['projects'][0]
                
                # Check budget for fixed projects
                if project.get('type') == 'fixed':
                    max_budget = project_data.get('budget', {}).get('maximum', 0)
                    if max_budget <= 30:
                        continue
                
                # Add to filtered projects
                filtered_projects.append({
                    'id': project_id,   
                    'owner_id': user_id,
                    'project_title': project_data.get('title'),
                    'project_description': project_data.get('description'),
                    'minimum_budget': project_data.get('budget', {}).get('minimum', 0),
                    'maximum_budget': project_data.get('budget', {}).get('maximum', 0),
                    'currency': currency_code,
                    'type': project.get('type'),
                    'exchange_rate': project.get("currency", {}).get("exchange_rate", 1),
                    'submitdate': project.get("submitdate"),
                    'seo_url': project.get("seo_url")
                })
                
            except Exception as e:
                print(f"Error getting complete details for project {project_id}: {e}")
                continue
        
        return filtered_projects
    
    def make_put_request(self, endpoint: str, headers: Dict[str, str] = None, 
                        params_data: Dict[str, Any] = None, form_data: Dict[str, Any] = None, 
                        json_data: Dict[str, Any] = None):
        """Make PUT request to Freelancer API"""
        url = f"{self.session.url}/{self.projects_endpoint}/{endpoint}"
        return self.session.session.put(
            url, 
            headers=headers, 
            params=params_data,
            data=form_data, 
            json=json_data, 
            verify=True
        )
    
    @retry_on_failure()
    def highlight_project_bid(self, bid_id: str) -> bool:
        """
        Highlight (seal) a project bid.
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        bid_data = {'action': 'seal'}
        endpoint = f'bids/{bid_id}'
        
        try:
            response = self.make_put_request(endpoint, headers=headers, params_data=bid_data)
            json_data = response.json()
            
            if response.status_code == 200:
                return json_data.get('status') == 'success'
            else:
                print(f"Error highlighting bid {bid_id}: {json_data.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Error highlighting bid {bid_id}: {e}")
            return False
    
    @retry_on_failure()
    def place_bid(self, project_id: str, bid_content: str, bid_amount: float, 
                  bid_period: int = 7) -> bool:
        """
        Place a bid on a project.
        """
        try:
            my_user_id = self.get_self_user_id()
            if not my_user_id:
                print("Could not get user ID")
                return False
            
            response = place_project_bid(
                self.session,
                project_id=project_id,
                bidder_id=my_user_id,
                amount=bid_amount,
                period=bid_period,
                milestone_percentage=100,
                description=bid_content
            )
            
            if response:
                print(f"✅ Successfully placed bid on project {project_id}")
                print(bid_content)
                
                # Try to highlight the bid
                try:
                    self.highlight_project_bid(str(response.id))
                except Exception as e:
                    print(f"❌ Error sealing bid {project_id}: {e}")
                
                return True
            else:
                print(f"⚠️ Failed to place bid on project {project_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error placing bid on project {project_id}: {e}")
            print(my_user_id)
            return False
    
    def process_project_bid(self, project: Dict[str, Any], bid_content: str, 
                           bid_amount: float, bid_period: int) -> bool:
        """
        Process a complete bid placement including waiting and logging.
        """
        # Wait if needed
        if project.get("submitdate"):
            wait_until_20_sec(project["submitdate"])
        
        # Place the bid
        success = self.place_bid(
            project["id"], 
            bid_content, 
            bid_amount, 
            bid_period
        )
        
        if success:
            # Generate project link for logging
            project_link = generate_project_link(project)
            print(f"Project Link: {project_link}")
        
        return success
