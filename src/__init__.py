"""
Freelancer Bot Package
"""

from .bot import FreelancerBot
from .config import *
from .models import *
from .database import DatabaseService
from .freelancer_service import FreelancerService
from .ai_service import AIService
from .utils import *

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Automated Freelancer.com bidding bot with AI-powered project analysis"

