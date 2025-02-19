from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects, get_projects, get_bids, place_project_bid
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
    create_get_projects_object,
    create_get_projects_project_details_object,
    create_get_projects_user_details_object
)
from freelancersdk.resources.users import get_self_user_id
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import re
from dotenv import load_dotenv
import time
import os


# -------------------------------
# Configuration
# -------------------------------
BID_LIMIT = 50
load_dotenv()

#URL = 'https://www.freelancer-sandbox.com'
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

session = Session(oauth_token=OAUTH_TOKEN)

llm = ChatGroq(api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

# Define Skill IDs and Language Codes
skill_ids = [3, 9, 13, 15, 17, 20, 21, 26, 32, 38, 44, 57, 69, 70, 77, 106, 107, 115, 116, 127, 137, 168, 170, 174, 196, 197, 204, 229, 232, 234, 247, 250, 262, 264, 277, 278, 284, 305, 310, 323, 324, 335, 359, 365, 368, 369, 371, 375, 408, 412, 433, 436, 444, 445, 482, 502, 564, 624, 662, 710, 759, 878, 950, 953, 959, 1063, 1185, 1314, 1623, 2071, 2128, 2222, 2245, 2338, 2342, 2507, 2586, 2587, 2589, 2605, 2625, 2645, 2673, 2698, 2717, 2745]
language_codes = ['en', 'it']

search_filter = create_search_projects_filter(
    jobs=skill_ids,
    languages=language_codes,
    sort_field='time_updated',
    or_search_query=True
)
unwanted_currencies = {"INR", "PKR", "BDT"}

# -------------------------------
# Step 1: Filter Projects
# -------------------------------

def filter_projects(session, projects):
    filtered_projects = []
    for project in projects:
        project_id = project.get('id')
        currency_code = project.get('currency', {}).get('code', '')
        # Skip unwanted currencies, projects already bid, NDA projects, or inactive ones.
        if currency_code in unwanted_currencies:
            # print("unwanted")
            # print(project.get('title'))
            continue
        if project.get('upgrades', False).get('NDA', False):
            # print("NDA")
            # print(project.get('title'))
            continue
        if project.get('status', '').lower() != 'active':
            # print("inactive")
            # print(project.get('title'))
            continue
        if project.get('type', '').lower() != 'fixed':
            # print("hourly")
            # print(project.get('title'))
            continue
        # Retain only the necessary fields.
        filtered_projects.append({
            'id': project_id,
            'owner_id': project.get('owner_id'),
            'title': project.get('title'),
            'preview_description': project.get('preview_description'),
            'budget': project.get('budget', {}),
            'currency': currency_code,
            'type': project.get('type'),
            'exchange_rate': project.get("currency", {}).get("exchange_rate", 1),
        })
    return filtered_projects

def has_placed_bid(session, project_id):
    try:
        response = get_bids(session, project_ids=[project_id])
        return bool(response.get('bids'))
    except Exception as e:
        print(f"Error checking bid status for project {project_id}: {e}")
        return False

# -------------------------------
# Step 2: LLM Refinement to Check Service Match
# -------------------------------
def check_project_match_with_llm(project):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional marketing analyst. Based on the project details provided, decide whether the project "
            "matches our service offerings. Respond with only 'MATCH' or 'NO MATCH'.\n"
            "Our Services: We specialize in website development and graphic design services including platforms like WordPress, "
            "HTML/CSS, E-Commerce, GoDaddy, Wix, Shopify, PHP and AI-driven websites. For graphic design, we provide vector illustrations, "
            "logo design, brochures, flyers, banners, etc."),
        ("human", "Project Title: {title}\nProject Description: {description}\n")
    ])
    chain = prompt | llm
    try:
        response = chain.invoke({
            "title": project["title"],
            "description": project["preview_description"]
        })
        return response.content.strip()
    except Exception as e:
        print(f"LLM evaluation error for project {project.get('id')}: {e}")
        return ""

def refine_projects_with_llm(projects):
    refined = []
    for project in projects:
        result = check_project_match_with_llm(project)
        # print(f"LLM evaluation for project {project['id']}: {result}")
        if result == "MATCH":
            refined.append(project)
    return refined

# -------------------------------
# Step 3a: LLM Analysis for Budget & Deadline
# -------------------------------
def analyze_budget_deadline(project):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert project analyst. analyze our base project budget and timeline
            Base Budget and Timeline details:
            Website Design & Development → $1,500 , 10 - 20 days
            Logo Design → $100, 2 - 7 days
            Custom Artwork → $150, 2 - 7 days
            E-commerce Development & Optimization → $2000 , 15 - 25 days
            UI/UX Design & User Engagement → $500, 7 - 11 days
            Vector illustration(each) → $150, 4 - 7 days
            _______
            above is the basic structure of budget and deadline but this is not fixed
            the budget can also increase according to the min-max budget of  client
            KEEP THIS IN MIND BUDGET SHOULD ALWAYS BE GREATER THEN MINUM BUDGET OF CLIENT NO MATTER WHAT
            above are the base budget and time according to this analyze the current
            project details, analyze and return the recommended budget"
            "and a proposed deadline (in days) for completion. Only output in the format: "
            "'Budget: <budget> USD, Deadline: <days> days'. Do not include any extra text."""),
        ("human", (
            "Project Title: {title}\n"
            "Project Description: {description}\n"
            "Minimum Budget: {budget_min}\n"
            "Maximum Budget: {budget_max}\n"
            "KEEP THIS IN MIND: BUDGET SHOULD ALWAYS BE GREATER THAN CLIENT'S MINIMUM BUDGET"
        ))
    ])
    chain = prompt | llm
    try:
        # Using preview_description as fallback if full description is missing.
        description = project.get('description', project.get('preview_description', ''))
        response = chain.invoke({
            "title": project["title"],
            "description": description,
            "budget_min": project.get('budget', {}).get('minimum', 0) * project.get("exchange_rate", 1),
            "budget_max": project.get('budget', {}).get('maximum', 0) * project.get("exchange_rate", 1),
        })
        return response.content.strip()
    except Exception as e:
        print(f"Error analyzing budget and deadline for project {project.get('id')}: {e}")
        return ""

# -------------------------------
# Step 3b: LLM Analysis for Bid Content (Exclude Budget)
# -------------------------------
def generate_bid_content(project):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """_______________________
Above are the details of the project Act as a professional marketing person and Write a personalized bid for the project Details provided Keep the below details in mind while writing a bid:
1) Analyze all the key requirements and details of the project before writing a personalized bid for the client according to the Project details
2) it should sound friendly and MAKE SURE IT DONT SOUND ROBOTIC
3) it should also sound confident
4) it should start with 1 line mentioning something like "First let me show you our previous work that aligns with your requirements" then showcase our previous work related to the project through max 3 links it should write a paragraph about the main core of the bid than on the next paragraph it should drop 1 or 2 questions related to the project followed with this
"I would love to chat with you about your project and believe 1-on-1 conversions are more effective.
warm Regards,
Inshal
*The budget and timeline are TBD* "
5) it should be concise and direct
6) do not repeat anything that is already mentioned in the Client bid so it doesn't sound boring
7) don't add a greeting at the start
8) Make it engaging so clients don't lose interest anywhere while reading
9) don't have to write anything about links after providing links
10) make sure that it is in proper formatting
11) just paste the link as It is
12) make it short concise and to the point
______________
below I'm providing you the links to my portfolio to use

Logo Design:
www.pinterest.com/sajidsaleem16/custom-logo-designs/
Custom Web Design:
www.behance.net/sajidsaleem16
Custom T-shirt Design:
www.pinterest.com/sajidsaleem16/custom-t-shirt-designs/
Brand Guide / Brand Identity / Business Cards:
www.pinterest.com/sajidsaleem16/style-guide-brand-guideline/
Custom Social Media Pack:
www.pinterest.com/sajidsaleem16/custom-social-media-pack-design/
Custom PPT Templates:
www.pinterest.com/sajidsaleem16/custom-ppt-template/
Custom Print Designs:
www.pinterest.com/sajidsaleem16/custom-print-designs/
Custom Packaging:
www.pinterest.com/sajidsaleem16/custom-packaging/
Custom Character & Mascot:
www.pinterest.com/sajidsaleem16/custom-character-mascot/
Custom Sticker packs:
www.pinterest.com/sajidsaleem16/custom-sticker-packs/
Custom Stationery Designs:
www.pinterest.com/sajidsaleem16/stationary-design/
General Design link:
www.pinterest.com/sajidsaleem16/
Profile link:
www.freelancer.com/u/SajidSaleem16
____________________________________________________________________________
Website Design / Development:
Please view my previous web development projects:
https://sajid-saleem.com/
https://velmontmedia.co.uk/
https://www.jqwholesale.com/
https://velmontrecords.co.uk/
https://edenarttattoo.com/
https://www.hoooyi.com/
https://mortgages-and-money.com/
https://itection.co/
https://ottawaods.ca/
https://www.buildmeapp.io/
https://turnuptechnologies.co/
https://voxcity.com/en
https://drilltalent.com/
https://wandaura.com/
https://skoolbellz.com/
https://trendyadore.com/
https://ab-zheng.com/
https://shahjukhowaja.com/
htttps://flcredithelp.com/

"""),
        ("human", "Project Title: {title}\nProject Description: {description}\n")
    ])
    chain = prompt | llm
    try:
        response = chain.invoke({
            "title": project["title"],
            "description": project["preview_description"],
        })
        return response.content.strip()
    except Exception as e:
        print(f"Error generating bid content for project {project.get('id')}: {e}")
        return ""

# -------------------------------
# Step 3c: Compose Custom Bid Template
# -------------------------------
def compose_bid_template(bid_content, budget_deadline_info):
    template = "{bid_content}\n\n{budget_deadline_info}"
    try:
        return template.format(
            bid_content=bid_content,
            budget_deadline_info=budget_deadline_info
        )
    except Exception as e:
        print(f"Error composing bid template: {e}")
        return bid_content

# -------------------------------
# Step 4: Process Projects to Generate Final Bids
# -------------------------------
def extract_budget_and_deadline(info):
    # Attempt to extract numbers from the LLM response.
    budget_match = re.search(r"Budget:\s*(\d+)", info)
    deadline_match = re.search(r"Deadline:\s*(\d+)", info)
    if budget_match and deadline_match:
        budget = int(budget_match.group(1))
        deadline = int(deadline_match.group(1))
        return budget, deadline
    else:
        print("Error: Unable to extract budget and deadline from info.")
        return None, None

def shortlist_projects_and_generate_bids(projects):
    shortlisted_bids = []
    for project in projects:
        try:
            rate = project.get("exchange_rate", 1)
            budget_deadline_info = analyze_budget_deadline(project)
            # print(f"Budget & Deadline analysis for project {project['id']}: {budget_deadline_info}")
            budget, deadline = extract_budget_and_deadline(budget_deadline_info)
            if budget is None or deadline is None:
                print(f"Skipping project {project['id']} due to missing budget/deadline info.")
                continue

            bid_content = generate_bid_content(project)
            # print(f"Bid content for project {project['id']}: {bid_content}")
            final_bid_message = compose_bid_template(bid_content, budget_deadline_info)
            bid_amount = (budget / rate) if rate else 1000

            shortlisted_bids.append({
                "project_id": project["id"],
                "bid_content": bid_content,
                "bid_amount": bid_amount,
                "bid_period": deadline,
                "currency_code": project.get("currency", "USD")
            })
        except Exception as e:
            print(f"Error processing project {project.get('id')}: {e}")
    return shortlisted_bids

# -------------------------------
# Step 5: Place Bids (Live Mode)
# -------------------------------
def place_bid(session, project_id, bid_content, bid_amount, bid_period=7):
    try:
        my_user_id = get_self_user_id(session)
    except Exception as e:
        print(f"Error getting self user ID: {e}")
        return
    try:
        response = place_project_bid(
            session,
            project_id=project_id,
            bidder_id=my_user_id,
            amount=bid_amount,
            period=bid_period,
            milestone_percentage=100,  # Adjust as needed
            description=bid_content
        )
        if response:
            print(f"✅ Successfully placed bid on project {project_id}")
        else:
            print(f"⚠️ Failed to place bid on project {project_id}. Response: {response}")
    except Exception as e:
        print(f"❌ Error placing bid on project {project_id}: {e}")

def auto_bid_on_projects(session, shortlisted_bids):
    for bid in shortlisted_bids:
        # print(f"🚀 Placing bid on Project {bid['project_id']}...")
        place_bid(session, bid["project_id"], bid["bid_content"], bid["bid_amount"], bid["bid_period"])

# -------------------------------
# Testing Function (Dry Run)
# -------------------------------
def test_bid_on_projects(shortlisted_bids):
    for bid in shortlisted_bids:
        print(f"\n---\nTEST MODE: Bid for Project {bid['project_id']}")
        print("Bid Content:")
        print(bid["bid_content"])
        print(f"Bid Amount: {bid['bid_amount']} {bid['currency_code']}")
        print("Deadline Analysis:")
        print(bid["bid_period"])
        print("---\n")