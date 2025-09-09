"""
Utility functions for the Freelancer Bot
"""
import time
import re
import logging
from typing import Dict, Any, Optional, Tuple
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry_on_failure(retry_count: int = 3, wait_seconds: int = 5):
    """
    A decorator that retries the execution of the function if an exception is raised.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Error in function '{func.__name__}', attempt {attempt} of {retry_count}: {e}")
                    if attempt < retry_count:
                        logger.info(f"Waiting for {wait_seconds} seconds before retrying...")
                        time.sleep(wait_seconds)
            raise Exception(f"Failed executing '{func.__name__}' after {retry_count} attempts")
        return wrapper
    return decorator

def wait_until_20_sec(project_submit_timestamp: float, min_wait: int = 32) -> None:
    """
    Wait until the specified time has passed since project posting.
    """
    current_time = time.time()
    elapsed = current_time - project_submit_timestamp
    wait = min_wait
    
    if elapsed < wait:
        wait_time = wait - elapsed
        wait_time = max(wait_time, 0)
        wait_time = min(wait_time, min_wait)
        wait_time = round(wait_time)
        logger.info(f"Waiting {wait_time:.2f} seconds until project is {wait} seconds old...")
        time.sleep(wait_time)

def extract_budget_and_deadline(info: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract budget and deadline from LLM response.
    """
    budget_match = re.search(r"Budget:\s*(\d+)", info)
    deadline_match = re.search(r"Deadline:\s*(\d+)", info)
    
    if budget_match and deadline_match:
        budget = int(budget_match.group(1))
        deadline = int(deadline_match.group(1))
        return budget, deadline
    else:
        logger.error("Unable to extract budget and deadline from info.")
        logger.error(info)
        return None, None

def generate_project_link(project: Dict[str, Any]) -> str:
    """
    Generate project link from project data.
    """
    base_url = "https://www.freelancer.com/projects"
    if project.get("seo_url"):
        return f"{base_url}/{project['seo_url']}/details"
    else:
        return f"{base_url}/{project['project_id']}"

def clean_llm_response(response: str) -> str:
    """
    Clean LLM response by removing thinking tags and extra whitespace.
    """
    cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return cleaned.strip()

def format_currency(amount: float, currency: str) -> str:
    """
    Format currency amount for display.
    """
    return f"{currency} {amount:.2f}"

def calculate_bid_amount(
    project: Dict[str, Any], 
    proposed_budget: Optional[int] = None
) -> float:
    """
    Calculate appropriate bid amount based on project details.
    """
    rate = project.get("exchange_rate", 1)
    min_budget = project.get("minimum_budget", 0)
    max_budget = project.get("maximum_budget", 0)
    project_type = project.get("type", "").lower()
    
    if project_type == "fixed":
        if proposed_budget:
            budget = max(70, proposed_budget)
            bid_amount = (budget / rate) if rate else 1000
            bid_amount = max(min_budget, bid_amount)
            bid_amount = min(max_budget, bid_amount) if max_budget else bid_amount
        else:
            bid_amount = max(70, (min_budget + max_budget) / 1.5)
            bid_amount = min(max_budget, bid_amount) if max_budget else bid_amount
    else:
        # Hourly project
        bid_amount = max(25, (max_budget + min_budget) / 2) if max_budget else 25
    
    return round(bid_amount, 2)

def validate_project_data(project: Dict[str, Any]) -> bool:
    """
    Validate that project has required fields.
    """
    required_fields = ["id", "project_title", "project_description", "minimum_budget"]
    return all(field in project and project[field] is not None for field in required_fields)

def sanitize_text(text: str) -> str:
    """
    Sanitize text for safe storage and display.
    """
    if not text:
        return ""
    
    # Remove or replace potentially problematic characters
    text = re.sub(r'[^\w\s\-.,!?@#$%&*()+=:;"\'<>/\\]', '', text)
    return text.strip()

def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable format.
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

