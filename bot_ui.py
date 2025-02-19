import streamlit as st
import time
import threading
from datetime import datetime

# Import your existing bot code
from bidding_bot_script import (  # Replace with your actual file name
    search_projects, filter_projects, refine_projects_with_llm,
    shortlist_projects_and_generate_bids, auto_bid_on_projects,
    BID_LIMIT, skill_ids, language_codes, unwanted_currencies
)

# Initialize session state variables
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_bids': 0,
        'projects_processed': 0,
        'matches_found': 0,
        'last_activity': 'Never'
    }
if 'active_projects' not in st.session_state:
    st.session_state.active_projects = []
if 'recent_bids' not in st.session_state:
    st.session_state.recent_bids = []

# Helper functions
def log_message(message, type='info'):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {type.upper()} - {message}"
    st.session_state.logs.append(log_entry)
    if len(st.session_state.logs) > 100:  # Keep last 100 logs
        st.session_state.logs.pop(0)

def update_stats(field, value=1):
    st.session_state.stats[field] += value
    st.session_state.stats['last_activity'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Bot control functions
def run_bot():
    processed_project_ids = set()
    
    while st.session_state.bot_running and st.session_state.stats['total_bids'] < st.session_state.bid_limit:
        try:
            # Main bot logic
            projects = search_projects(st.session_state.session, query='', search_filter=st.session_state.search_filter)
            new_projects = [p for p in projects['projects'] if p.get('id') not in processed_project_ids]
            
            for p in new_projects:
                processed_project_ids.add(p.get('id'))
                update_stats('projects_processed')
            
            filtered_projects = filter_projects(st.session_state.session, new_projects)
            refined_projects = refine_projects_with_llm(filtered_projects)
            shortlisted_bids = shortlist_projects_and_generate_bids(refined_projects)
            
            if shortlisted_bids:
                st.session_state.active_projects = [{
                    'id': p['id'],
                    'title': p['title'],
                    'budget': f"{p['budget'].get('minimum', '?')}-{p['budget'].get('maximum', '?')} {p['currency']}",
                    'status': 'Pending Bid'
                } for p in refined_projects][-10:]  # Keep last 10 projects
                
                for bid in shortlisted_bids:
                    if st.session_state.stats['total_bids'] >= st.session_state.bid_limit:
                        break
                    
                    try:
                        auto_bid_on_projects(st.session_state.session, [bid])
                        st.session_state.recent_bids.append({
                            'project_id': bid['project_id'],
                            'amount': bid['bid_amount'],
                            'status': 'Success',
                            'time': datetime.now().strftime("%H:%M:%S")
                        })
                        update_stats('total_bids')
                        log_message(f"Bid placed on project {bid['project_id']}")
                    except Exception as e:
                        log_message(f"Bid failed: {str(e)}", 'error')
                    
                    time.sleep(st.session_state.bid_delay)
            
            time.sleep(st.session_state.search_interval)
        
        except Exception as e:
            log_message(f"Bot error: {str(e)}", 'error')
            time.sleep(10)
    
    st.session_state.bot_running = False

# Streamlit UI Layout
st.set_page_config(page_title="Auto Bid Bot Dashboard", layout="wide")
# Update the session state initialization section
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_bids': 0,
        'projects_processed': 0,
        'matches_found': 0,
        'last_activity': 'Never'
    }
if 'active_projects' not in st.session_state:
    st.session_state.active_projects = []
if 'recent_bids' not in st.session_state:
    st.session_state.recent_bids = []
# Add these new session state entries
if 'bid_limit' not in st.session_state:
    st.session_state.bid_limit = BID_LIMIT  # Your default value from constants
if 'search_interval' not in st.session_state:
    st.session_state.search_interval = 300
if 'bid_delay' not in st.session_state:
    st.session_state.bid_delay = 20
# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    
    # Bot Settings
    st.subheader("Bot Settings")
    st.session_state.bid_limit = st.number_input(
        "Daily Bid Limit", 
        min_value=1, 
        max_value=50, 
        value=st.session_state.bid_limit
    )
    st.session_state.search_interval = st.number_input(
        "Search Interval (seconds)", 
        min_value=60, 
        value=st.session_state.search_interval
    )
    st.session_state.bid_delay = st.number_input(
        "Delay Between Bids (seconds)", 
        min_value=10, 
        value=st.session_state.bid_delay
    )
    
    # API Configuration
    st.subheader("API Configuration")
    oauth_token = st.text_input("Freelancer OAuth Token", type="password")
    groq_key = st.text_input("Groq API Key", type="password")
    
    # Skill Configuration
    st.subheader("Skill Filters")
    with st.expander("Advanced Filters"):
        st.multiselect("Skills", skill_ids, default=skill_ids)
        st.multiselect("Languages", language_codes, default=language_codes)
        st.multiselect("Blocked Currencies", unwanted_currencies, default=unwanted_currencies)

# Main Dashboard
st.title("Auto Bid Bot Dashboard")

# Control Row
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("▶️ Start Bot", disabled=st.session_state.bot_running):
        st.session_state.bot_running = True
        threading.Thread(target=run_bot).start()
        log_message("Bot started")

with col2:
    if st.button("⏹️ Stop Bot", disabled=not st.session_state.bot_running):
        st.session_state.bot_running = False
        log_message("Bot stopped")

with col3:
    st.metric("Bids Placed Today", 
         f"{st.session_state.stats['total_bids']}/{st.session_state.bid_limit}",
         help="Daily bid counter")

# Statistics Cards
st.subheader("Real-time Statistics")
stats_cols = st.columns(4)
stats_cols[0].metric("Total Projects Processed", st.session_state.stats['projects_processed'])
stats_cols[1].metric("Successful Matches", st.session_state.stats['matches_found'])
stats_cols[2].metric("Recent Bid Success Rate", 
                    f"{len([b for b in st.session_state.recent_bids if b['status'] == 'Success'])*10}%")
stats_cols[3].metric("Last Activity", st.session_state.stats['last_activity'])

# Project Information
tab1, tab2, tab3 = st.tabs(["Active Projects", "Bid History", "System Logs"])

with tab1:
    st.dataframe(
        data=st.session_state.active_projects,
        column_config={
            "id": "Project ID",
            "title": "Project Title",
            "budget": "Budget Range",
            "status": {"label": "Status", "help": "Current project status"}
        },
        use_container_width=True
    )

with tab2:
    st.dataframe(
        data=st.session_state.recent_bids[-10:],  # Show last 10 bids
        column_config={
            "project_id": "Project ID",
            "amount": {"label": "Bid Amount", "format": "$%.2f"},
            "status": "Status",
            "time": "Time"
        },
        use_container_width=True
    )

with tab3:
    st.code("\n".join(st.session_state.logs[-20:]), line_numbers=True)

# Live Status
st.subheader("Live Monitoring")
status_col1, status_col2 = st.columns(2)

with status_col1:
    st.radio("Bot Status", 
            ["Running" if st.session_state.bot_running else "Stopped"], 
            key="status_display")

with status_col2:
    st.progress(st.session_state.stats['total_bids'] / st.session_state.bid_limit, 
               text="Daily Bid Progress")

# Style Tweaks
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    [data-testid="stProgress"] > div > div > div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)