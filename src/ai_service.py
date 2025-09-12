"""
AI service for project analysis and bid generation
"""
import re
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from .config import GROQ_API_KEY, BASE_PROJECT_COMPONENTS, PORTFOLIO_LINKS, SERVICE_OFFERINGS, BID_WRITING_STYLE, PORTFOLIO_LINKS_TEXT, SIGNATURE
from .config_manager import config_manager
from .utils import retry_on_failure, clean_llm_response

class AIService:
    def __init__(self, config_manager_instance=None):
        # Use session-specific config manager or fallback to global
        self.config_manager = config_manager_instance or config_manager
        
        # Use configurable API key or fallback to default
        api_key = self.config_manager.get_groq_api_key() or GROQ_API_KEY
        self.llm = ChatGroq(api_key=api_key, model_name="qwen/qwen3-32b")
    
    @retry_on_failure()
    def check_project_match(self, project: Dict[str, Any]) -> str:
        """
        Check if project matches our service offerings using LLM.
        """
        # Use configurable service offerings or fallback to default
        service_offerings = self.config_manager.get_service_offerings() or SERVICE_OFFERINGS
        
        system_prompt = f"""You are a professional project analyst. Evaluate the following project details and decide whether the project matches our service offerings. Respond with only 'MATCH' or 'NO MATCH'. If you are not completely sure about the project details, respond with 'NO MATCH'.

Our Service Offerings:
{service_offerings}

Only return 'MATCH' if the project description clearly fits these criteria. Otherwise, return 'NO MATCH'."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Project Title: {title}\nProject Description: {description}\nMinimum Budget: {minimum_budget}\nMaximum Budget: {maximum_budget}\n")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "title": project["project_title"],
            "description": project["project_description"],
            'minimum_budget': project["minimum_budget"],
            'maximum_budget': project["maximum_budget"],
        })
        
        return clean_llm_response(response.content)

    @retry_on_failure()
    def analyze_budget_deadline(self, project: Dict[str, Any]) -> str:
        """
        Analyze project budget and deadline using LLM.
        """
        if project['type'].lower() != 'fixed':
            return 'None'
        
        # Create base components text
        base_components_text = "\n".join([
            f"- {name.replace('_', ' ').title()}: ${data['budget']}, {data['timeline']} days"
            for name, data in BASE_PROJECT_COMPONENTS.items()
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert project analyst. Below are the base project components with their associated budget and timeline:
{base_components_text}
IMPORTANT NOTE:
set the DEADLINE EXACT AS THE DEADLINE SUGGESTED IN ABOVE RECOMMENDED BUDGET
________________________
Using these as your baseline, analyze the client's budget range and adjust the recommended project budget and deadline according to the following guidelines:
1. The recommended budget must always be greater than or equal to the client's minimum budget.
2. analyze the details very carfully and if it include more work then the client max budget then you can propose higher budget for that according to the requirments
2. If the client's maximum budget is higher than the base budget, increase the recommended budget proportionally—but remain close to the base budget to keep it attractive and realistic.
3. The project deadline should be close to the base project timeline, without extending it unnecessarily.
4. For very low client budget ranges (e.g., $10–$30), do not generate an unrealistically high budget.
5. Make sure to set the deadline close or exact to the recommended project deadline.
6. Provide your final output in the exact format:
   "Budget: <budget> USD, Deadline: <days> days"

No additional text should be included in the output."""),
            ("human", (
                "Project Title: {title}\n"
                "Project Description: {description}\n"
                "Minimum Budget: {budget_min}\n"
                "Maximum Budget: {budget_max}\n"
                "OUTPUT SHOULD ONLY BE IN THE FORMAT 'Budget: <budget> USD, Deadline: <days> days'. DO NOT INCLUDE ANY EXTRA TEXT. "
                "KEEP THIS IN MIND: BUDGET SHOULD ALWAYS BE GREATER THAN THE CLIENT'S MINIMUM BUDGET."
            ))
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "title": project["project_title"],
            "description": project["project_description"],
            "budget_min": project["minimum_budget"] * project["exchange_rate"],
            "budget_max": project["maximum_budget"] * project["exchange_rate"],
        })
        
        return clean_llm_response(response.content)

    @retry_on_failure()
    def generate_bid_content(self, project: Dict[str, Any]) -> str:
        """
        Generate bid content using LLM.
        """
        # Use configurable portfolio links or fallback to default
        portfolio_links_text = self.config_manager.get_portfolio_links() or PORTFOLIO_LINKS_TEXT or "\n".join([
            f"{i+1}. {name.replace('_', ' ')} : {link}"
            for i, (name, link) in enumerate(PORTFOLIO_LINKS.items())
        ])
        
        # Use configurable bid writing style or fallback to default
        bid_style = self.config_manager.get_bid_writing_style() or BID_WRITING_STYLE
        signature = self.config_manager.get_signature() or SIGNATURE
        system_prompt = bid_style.format(signature=signature)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f'''{system_prompt}

Portfolio LINKS:
{portfolio_links_text}
'''),
            ("human", "Project Title: {title}\nProject Description: {description}\n")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "title": project["project_title"],
            "description": project["project_description"],
        })
        
        return clean_llm_response(response.content)

    def compose_bid_template(self, bid_content: str) -> str:
        """
        Compose final bid template.
        """
        template = "{bid_content}{budget_deadline_info}"
        try:
            return template.format(
                bid_content=bid_content,
                budget_deadline_info=""
            )
        except Exception as e:
            print(f"Error composing bid template: {e}")
            return bid_content