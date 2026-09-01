import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import calendar as cal
import os
import csv
from io import StringIO

# Clear caches on app reload
st.cache_data.clear()
st.cache_resource.clear()

TEAM_MEMBERS = [
    "John Bai",
    "Katherine Chen",
    "Yianni Mannias",
    "Masashi Tsuneizumi",
    "Ankit Sharma",
    "Nishant Patnaik"
]

ROLES = ["Lead", "Emcee", "Facilitator", "Moderator", "Support"]

EVENT_TYPES = {
    "Hands on Experiences": "hands_on",
    "Leaves": "leaves",
    "AI Assisted Agentic Development": "ai_agentic",
    "Lunch and Learns": "lunch_learn",
    "Blueprint Workshops": "blueprint_workshop",
    "GTM Onboarding": "gtm_onboarding",
    "Useful Links": "useful_links"
}

# Color scheme for different event types
EVENT_COLORS = {
    "Hands on Experiences": "#FFB6C1",  # Light Pink
    "Leaves": "#87CEEB",                # Sky Blue
    "AI Assisted Agentic Development": "#98FB98",  # Light Green
    "Lunch and Learns": "#FFD700",      # Gold
    "Blueprint Workshops": "#DDA0DD",   # Plum
    "GTM Onboarding": "#FFA500",        # Orange
}

EVENT_EMOJIS = {
    "Hands on Experiences": "🎓",
    "Leaves": "📴",
    "AI Assisted Agentic Development": "🤖",
    "Lunch and Learns": "🥗",
    "Blueprint Workshops": "🎪",
    "GTM Onboarding": "🚀",
}

THEMES = {
    "Ocean Blue": {
        "primary": "#5A9FD4",
        "secondary": "#E8F4F8",
        "accent": "#3B7CA8",
        "calendar_bg": "#E8F4F8",
        "calendar_border": "#5A9FD4"
    },
    "Forest Green": {
        "primary": "#7CB342",
        "secondary": "#F1F8E9",
        "accent": "#558B2F",
        "calendar_bg": "#F1F8E9",
        "calendar_border": "#7CB342"
    },
    "Sunset Orange": {
        "primary": "#FFB74D",
        "secondary": "#FFF3E0",
        "accent": "#FFA726",
        "calendar_bg": "#FFF3E0",
        "calendar_border": "#FFB74D"
    },
    "Purple Royale": {
        "primary": "#BA68C8",
        "secondary": "#F3E5F5",
        "accent": "#AB47BC",
        "calendar_bg": "#F3E5F5",
        "calendar_border": "#BA68C8"
    },
    "Modern Slate": {
        "primary": "#90A4AE",
        "secondary": "#F5F5F5",
        "accent": "#78909C",
        "calendar_bg": "#F5F5F5",
        "calendar_border": "#90A4AE"
    }
}

@st.cache_resource
def get_google_sheets_client():
    """Initialize Google Sheets client."""
    try:
        import json

        creds = None
        # Try different secret formats
        if "GOOGLE_SERVICE_ACCOUNT_JSON_STR" in st.secrets:
            # If stored as JSON string
            creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON_STR"])
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive']
            )
        elif "GOOGLE_SERVICE_ACCOUNT_JSON" in st.secrets:
            # If stored as TOML object
            creds = Credentials.from_service_account_info(
                st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"],
                scopes=['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive']
            )
        else:
            # Fallback to local file (for local development)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            creds_path = os.path.join(script_dir, "credentials.json")
            creds = Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive']
            )

        if creds:
            client = gspread.authorize(creds)
            return client
        return None
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

@st.cache_data(ttl=300)
def load_events():
    """Load events from Google Sheets."""
    client = get_google_sheets_client()
    if not client:
        return pd.DataFrame()

    try:
        sheet_id = st.secrets["GOOGLE_SHEETS_ID"]
        spreadsheet = client.open_by_key(sheet_id)

        all_events = []
        for worksheet in spreadsheet.worksheets():
            if worksheet.title != "Useful Links":
                try:
                    data = worksheet.get_all_records()
                    for record in data:
                        record['event_type'] = worksheet.title
                    all_events.extend(data)
                except:
                    pass

        return pd.DataFrame(all_events) if all_events else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_useful_links():
    """Load useful links from Google Sheets."""
    client = get_google_sheets_client()
    if not client:
        return pd.DataFrame()

    try:
        sheet_id = st.secrets["GOOGLE_SHEETS_ID"]
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet("Useful Links")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

def save_event_to_sheets(event_data, event_type_name):
    """Save event to Google Sheets."""
    client = get_google_sheets_client()
    if not client:
        st.error("Cannot connect to Google Sheets")
        return False

    # Define column order for each event type
    COLUMN_ORDER = {
        "Hands on Experiences": ["name", "description", "id", "date", "location", "experiences", "sa_id", "itsm_ticket", "num_assets", "gameboard_url", "invite_demox", "invite_demoexperiences", "assignees", "travel_required", "engagement_app_entry", "created"],
        "Leaves": ["name", "description", "id", "from_date", "to_date", "created"],
        "AI Assisted Agentic Development": ["name", "description", "id", "date", "sa_id", "pre_work_done", "assignees", "travel_required", "engagement_app_entry", "created"],
        "Lunch and Learns": ["name", "description", "id", "date", "sa_id", "topic", "useful_link", "assignees", "travel_required", "engagement_app_entry", "created"],
        "Blueprint Workshops": ["name", "description", "id", "workshop_type", "from_date", "to_date", "platform", "sa_id", "assignees", "travel_required", "engagement_app_entry", "created"],
        "GTM Onboarding": ["name", "description", "id", "date", "sa_id", "topic", "useful_link", "assignees", "travel_required", "engagement_app_entry", "created"],
        "Useful Links": ["id", "title", "url", "category", "created"]
    }

    try:
        sheet_id = st.secrets["GOOGLE_SHEETS_ID"]
        spreadsheet = client.open_by_key(sheet_id)

        try:
            worksheet = spreadsheet.worksheet(event_type_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=event_type_name, rows=100, cols=20)

        headers = COLUMN_ORDER.get(event_type_name, list(event_data.keys()))
        if not worksheet.row_values(1):
            worksheet.insert_row(headers)

        values = [str(event_data.get(h, "")) for h in headers]
        worksheet.append_row(values)

        st.session_state.success_message = "✅ Event saved successfully!"
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving event: {str(e)}")
        return False

def delete_event_from_sheets(event_type_name, event_id):
    """Delete event from Google Sheets."""
    client = get_google_sheets_client()
    if not client:
        return False

    try:
        sheet_id = st.secrets["GOOGLE_SHEETS_ID"]
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(event_type_name)

        cell_list = worksheet.findall(event_id)
        if cell_list:
            worksheet.delete_rows(cell_list[0].row)
            st.session_state.success_message = "✅ Event deleted successfully!"
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting event: {e}")
        return False

def get_events_for_date(date_str, events_df):
    """Get all events for a specific date."""
    if events_df.empty:
        return pd.DataFrame()

    events_df = events_df.reset_index(drop=True)
    date_events = []

    for idx, row in events_df.iterrows():
        if 'from_date' in row and 'to_date' in row:
            try:
                from_date = pd.to_datetime(row['from_date'], errors='coerce')
                to_date = pd.to_datetime(row['to_date'], errors='coerce')
                check_date = pd.to_datetime(date_str, errors='coerce')

                if from_date <= check_date <= to_date:
                    date_events.append(idx)
            except:
                pass

        if 'date' in row:
            try:
                if pd.to_datetime(row['date'], errors='coerce').strftime('%Y-%m-%d') == date_str:
                    date_events.append(idx)
            except:
                pass

    if date_events:
        return events_df.iloc[date_events]
    return pd.DataFrame()

def render_calendar_month(year, month, theme_colors=None):
    """Render month view calendar with clickable dates and color coding."""
    if theme_colors is None:
        theme_colors = THEMES.get("Ocean Blue", {})

    events_df = load_events()

    month_calendar = cal.monthcalendar(year, month)
    month_name = cal.month_name[month]

    st.subheader(f"{month_name} {year}")

    # Visual Legend with color boxes
    st.markdown("**Color Legend:**")
    legend_cols = st.columns(5)

    event_types_legend = [
        ("🎓 Hands on", EVENT_COLORS["Hands on Experiences"]),
        ("📴 Leaves", EVENT_COLORS["Leaves"]),
        ("🤖 AI Agentic", EVENT_COLORS["AI Assisted Agentic Development"]),
        ("🥗 Lunch & Learn", EVENT_COLORS["Lunch and Learns"]),
        ("🎪 Workshops", EVENT_COLORS["Blueprint Workshops"]),
        ("🚀 GTM Onboarding", EVENT_COLORS["GTM Onboarding"])
    ]

    for col, (label, color) in zip(legend_cols, event_types_legend):
        with col:
            st.markdown(f"""
            <div style='background-color: {color}; border: 2px solid #333; border-radius: 5px; padding: 12px; text-align: center; font-weight: bold;'>
                {label}
            </div>
            """, unsafe_allow_html=True)

    # Apply calendar styling
    calendar_bg = theme_colors.get("calendar_bg", "#e6f2ff")
    calendar_border = theme_colors.get("calendar_border", "#0066cc")

    st.markdown(f"""
    <style>
    .calendar-container {{
        background-color: {calendar_bg};
        border: 3px solid {calendar_border};
        border-radius: 8px;
        padding: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Days header
    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for col, day in zip(cols, days):
        with col:
            st.markdown(f"<div style='text-align: center; font-weight: bold; border-bottom: 2px solid {calendar_border}; padding: 10px;'>{day}</div>", unsafe_allow_html=True)

    for week in month_calendar:
        cols = st.columns(7)
        for col, day in zip(cols, week):
            with col:
                if day == 0:
                    st.markdown("<div style='height: 100px; border: 1px solid #ddd;'></div>", unsafe_allow_html=True)
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    day_events = get_events_for_date(date_str, events_df)
                    event_count = len(day_events)

                    # Get dominant event type for color
                    cell_bg = "#ffffff"
                    event_icons = ""
                    if not day_events.empty:
                        cell_bg = EVENT_COLORS.get(day_events.iloc[0]['event_type'], "#ffffff")
                        for _, evt in day_events.iterrows():
                            emoji = EVENT_EMOJIS.get(evt['event_type'], "📌")
                            event_icons += emoji

                    button_text = f"{day}\n{event_icons}\n({event_count})"

                    # Create styled button with border
                    if col.button(button_text, key=f"date_{date_str}", use_container_width=True):
                        st.session_state.selected_date = date_str
                        st.rerun()

def display_event_details(event, event_type):
    """Display event details in business-readable format."""
    if 'description' in event and event['description']:
        st.warning(f"📝 **Description:**\n\n{event['description']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if event_type == "Hands on Experiences":
            if 'from_date' in event and event['from_date']:
                st.write(f"**Start Date:** {event['from_date']}")
            if 'to_date' in event and event['to_date']:
                st.write(f"**End Date:** {event['to_date']}")
            if 'location' in event and event['location']:
                st.write(f"**Location:** {event['location']}")
            if 'experiences' in event and event['experiences']:
                st.write(f"**Experiences:** {event['experiences']}")
            if 'gameboard_url' in event and event['gameboard_url']:
                st.write(f"**Gameboard URL:** [{event['gameboard_url']}]({event['gameboard_url']})")
            if 'invite_demox' in event:
                status = "✅ Sent" if event['invite_demox'] else "❌ Not sent"
                st.write(f"**Calendar Invite (demoX@pega.com):** {status}")
            if 'invite_demoexperiences' in event:
                status = "✅ Sent" if event['invite_demoexperiences'] else "❌ Not sent"
                st.write(f"**Calendar Invite (demoexperiences@pega.com):** {status}")
                
        elif event_type == "Leaves":
            if 'resource_name' in event and event['resource_name']:
                st.write(f"**Resource:** {event['resource_name']}")
            if 'from_date' in event and event['from_date']:
                st.write(f"**From Date:** {event['from_date']}")
            if 'to_date' in event and event['to_date']:
                st.write(f"**To Date:** {event['to_date']}")
            if 'leave_type' in event and event['leave_type']:
                st.write(f"**Leave Type:** {event['leave_type']}")
                
        elif event_type == "AI Assisted Agentic Development":
            if 'date' in event and event['date']:
                st.write(f"**Date:** {event['date']}")
            if 'sa_id' in event and event['sa_id']:
                st.write(f"**SA ID:** {event['sa_id']}")
            if 'pre_work_done' in event:
                st.write(f"**Pre-work Done:** {event['pre_work_done']}")
                
        elif event_type == "Lunch and Learns":
            if 'date' in event and event['date']:
                st.write(f"**Date:** {event['date']}")
            if 'topic' in event and event['topic']:
                st.write(f"**Topic:** {event['topic']}")
            if 'sa_id' in event and event['sa_id']:
                st.write(f"**SA ID:** {event['sa_id']}")
            if 'useful_link' in event and event['useful_link']:
                st.write(f"**Useful Link:** {event['useful_link']}")

        elif event_type == "GTM Onboarding":
            if 'date' in event and event['date']:
                st.write(f"**Date:** {event['date']}")
            if 'topic' in event and event['topic']:
                st.write(f"**Topic:** {event['topic']}")
            if 'sa_id' in event and event['sa_id']:
                st.write(f"**SA ID:** {event['sa_id']}")
            if 'useful_link' in event and event['useful_link']:
                st.write(f"**Useful Link:** {event['useful_link']}")
                
        elif event_type == "Blueprint Workshops":
            if 'workshop_name' in event and event['workshop_name']:
                st.write(f"**Workshop Name:** {event['workshop_name']}")
            if 'from_date' in event and event['from_date']:
                st.write(f"**Start Date:** {event['from_date']}")
            if 'to_date' in event and event['to_date']:
                st.write(f"**End Date:** {event['to_date']}")
            if 'platform' in event and event['platform']:
                st.write(f"**Platform:** {event['platform']}")
    
    with col2:
        if event_type in ["Hands on Experiences"]:
            if 'assignees' in event and event['assignees']:
                st.write(f"**Assignees:** {event['assignees']}")
            if 'travel_required' in event and event['travel_required']:
                st.write(f"**Travel Required:** {event['travel_required']}")
            if 'sa_id' in event and event['sa_id']:
                st.write(f"**SA ID:** {event['sa_id']}")
            if 'itsm_ticket' in event and event['itsm_ticket']:
                st.write(f"**ITSM Ticket:** {event['itsm_ticket']}")
            if 'num_assets' in event and event['num_assets']:
                st.write(f"**Number of Assets:** {event['num_assets']}")
                
        elif event_type == "Blueprint Workshops":
            if 'assignees' in event and event['assignees']:
                st.write(f"**Assignees:** {event['assignees']}")
            if 'travel_required' in event and event['travel_required']:
                st.write(f"**Travel Required:** {event['travel_required']}")
        
        elif event_type in ["AI Assisted Agentic Development", "Lunch and Learns"]:
            if 'assignees' in event and event['assignees']:
                st.write(f"**Assignees:** {event['assignees']}")
            if 'travel_required' in event and event['travel_required']:
                st.write(f"**Travel Required:** {event['travel_required']}")
        


def show_events_for_date(selected_date, events_df):
    """Show events for a selected date."""
    st.subheader(f"📅 Events for {selected_date}")
    
    date_events = get_events_for_date(selected_date, events_df)
    
    if date_events.empty:
        st.info("No events on this date")
    else:
        for idx, row in date_events.iterrows():
            event_type = row.get('event_type', 'Unknown')
            description = row.get('description', 'No description')[:100]  # First 100 chars
            emoji = EVENT_EMOJIS.get(event_type, "📌")
            
            with st.expander(f"{emoji} {description}...", expanded=True):
                col1, col2 = st.columns([4, 1])

                with col1:
                    display_event_details(row, event_type)

                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        if delete_event_from_sheets(event_type, row.get('id', '')):
                            st.rerun()

def form_hands_on_experiences():
    """Form for Hands on Experiences."""
    st.subheader("Add Hands on Experiences")

    with st.form("hands_on_form"):
        event_name = st.text_input("Event Name *", key="hands_on_name")
        description = st.text_area("Description *", height=100, key="hands_on_desc")

        date = st.date_input("Date *", key="hands_on_date")
        location = st.text_input("Location *", key="hands_on_loc")

        st.write("Experiences (select all applicable) *")
        experiences = st.multiselect(
            "Experiences",
            ["Customer service", "Back Office", "Infinity Studio", "Agentic", "CDH/BP", "Blueprint legacy transformation experience"],
            key="hands_on_exp"
        )

        sa_id = st.text_input("SA ID", key="hands_on_sa")
        itsm_ticket = st.text_input("ITSM Ticket Number *", key="hands_on_itsm")
        num_assets = st.number_input("Number of assets required", min_value=0, key="hands_on_assets")

        gameboard_url = st.text_input("Gameboard URL *", key="hands_on_gameboard")

        st.write("**Calendar Invites (Check all that apply) ***")
        col_invite1, col_invite2 = st.columns(2)
        with col_invite1:
            invite_demox = st.checkbox("Sent to demoX@pega.com", key="invite_demox")
        with col_invite2:
            invite_demoexp = st.checkbox("Sent to demoexperiences@pega.com", key="invite_demoexp")

        st.write("**Assignees (Multi-select)**")
        assignees = st.multiselect("Select Assignees", TEAM_MEMBERS, key="hands_on_assignee")

        travel = st.checkbox("Travel Required", key="hands_on_travel")
        engagement_app = st.checkbox("Create entry in Engagement App", key="hands_on_engagement")

        submitted = st.form_submit_button("Save Event")

        if submitted:
            if not (event_name and description and date and location and experiences and itsm_ticket and assignees and gameboard_url and invite_demox and invite_demoexp):
                st.error("Please fill all mandatory fields")
            else:
                event_data = {
                    "name": event_name,
                    "description": description,
                    "id": f"hands_on_{datetime.now().timestamp()}",
                    "date": date.strftime("%Y-%m-%d"),
                    "location": location,
                    "experiences": ", ".join(experiences),
                    "sa_id": sa_id,
                    "itsm_ticket": itsm_ticket,
                    "num_assets": num_assets,
                    "gameboard_url": gameboard_url,
                    "invite_demox": invite_demox,
                    "invite_demoexperiences": invite_demoexp,
                    "assignees": ", ".join(assignees),
                    "travel_required": travel,
                    "engagement_app_entry": engagement_app,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "Hands on Experiences"):
                    st.rerun()

def form_pto():
    """Form for Leaves."""
    st.subheader("Add Leave")

    with st.form("pto_form"):
        resource_name = st.selectbox("Resource Name *", TEAM_MEMBERS, key="pto_resource")
        description = st.text_area("Description *", height=100, key="pto_desc")

        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From Date *", key="pto_from")
        with col2:
            to_date = st.date_input("To Date *", key="pto_to")

        leave_type = st.selectbox("Type of Leave *", ["Sick", "Personal", "Carers", "Bereavement", "Maternity", "Paternity"], key="pto_type")

        submitted = st.form_submit_button("Save PTO")

        if submitted:
            if not (resource_name and description and from_date and to_date and leave_type):
                st.error("Please fill all mandatory fields")
            elif to_date < from_date:
                st.error("❌ To Date must be after From Date")
            else:
                event_data = {
                    "name": f"{resource_name} - {leave_type}",
                    "description": description,
                    "id": f"pto_{datetime.now().timestamp()}",
                    "resource_name": resource_name,
                    "from_date": from_date.strftime("%Y-%m-%d"),
                    "to_date": to_date.strftime("%Y-%m-%d"),
                    "leave_type": leave_type,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "Leaves"):
                    st.rerun()

def form_ai_agentic():
    """Form for AI Assisted Agentic Development Experience."""
    st.subheader("Add AI Assisted Agentic Development Experience")

    with st.form("ai_agentic_form"):
        event_name = st.text_input("Event Name *", key="ai_name")
        description = st.text_area("Description *", height=100, key="ai_desc")
        date = st.date_input("Date *", key="ai_date")
        sa_id = st.text_input("SA ID *", key="ai_sa")
        pre_work = st.checkbox("Pre work done *", key="ai_prework")

        st.write("**Assignees (Multi-select)**")
        assignees = st.multiselect("Select Assignees", TEAM_MEMBERS, key="ai_agentic_assignee")

        travel = st.checkbox("Travel Required", key="ai_travel")
        engagement_app = st.checkbox("Create entry in Engagement App", key="ai_engagement")

        submitted = st.form_submit_button("Save Event")

        if submitted:
            if not (event_name and description and date and sa_id and assignees):
                st.error("Please fill all mandatory fields")
            else:
                event_data = {
                    "name": event_name,
                    "description": description,
                    "id": f"ai_agentic_{datetime.now().timestamp()}",
                    "date": date.strftime("%Y-%m-%d"),
                    "sa_id": sa_id,
                    "pre_work_done": pre_work,
                    "assignees": ", ".join(assignees),
                    "travel_required": travel,
                    "engagement_app_entry": engagement_app,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "AI Assisted Agentic Development"):
                    st.rerun()

def form_lunch_learn():
    """Form for Lunch and Learns."""
    st.subheader("Add Lunch and Learn")

    with st.form("lunch_learn_form"):
        event_name = st.text_input("Event Name *", key="lunch_name")
        description = st.text_area("Description *", height=100, key="lunch_desc")
        date = st.date_input("Date *", key="lunch_date")
        sa_id = st.text_input("SA ID *", key="lunch_sa")
        topic = st.text_input("Topic *", key="lunch_topic")
        useful_link = st.text_input("Useful links", key="lunch_link")

        st.write("**Assignees (Multi-select)**")
        assignees = st.multiselect("Select Assignees", TEAM_MEMBERS, key="lunch_learn_assignee")

        travel = st.checkbox("Travel Required", key="lunch_travel")
        engagement_app = st.checkbox("Create entry in Engagement App", key="lunch_engagement")

        submitted = st.form_submit_button("Save Event")

        if submitted:
            if not (event_name and description and date and sa_id and topic and assignees):
                st.error("Please fill all mandatory fields")
            else:
                event_data = {
                    "name": event_name,
                    "description": description,
                    "id": f"lunch_learn_{datetime.now().timestamp()}",
                    "date": date.strftime("%Y-%m-%d"),
                    "sa_id": sa_id,
                    "topic": topic,
                    "useful_link": useful_link,
                    "assignees": ", ".join(assignees),
                    "travel_required": travel,
                    "engagement_app_entry": engagement_app,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "Lunch and Learns"):
                    st.rerun()

def form_gtm_onboarding():
    """Form for GTM Onboarding."""
    st.subheader("Add GTM Onboarding")

    with st.form("gtm_onboarding_form"):
        event_name = st.text_input("Event Name *", key="gtm_name")
        description = st.text_area("Description *", height=100, key="gtm_desc")
        date = st.date_input("Date *", key="gtm_date")
        sa_id = st.text_input("SA ID *", key="gtm_sa")
        topic = st.text_input("Topic *", key="gtm_topic")
        useful_link = st.text_input("Useful links", key="gtm_link")

        st.write("**Assignees (Multi-select)**")
        assignees = st.multiselect("Select Assignees", TEAM_MEMBERS, key="gtm_assignee")

        travel = st.checkbox("Travel Required", key="gtm_travel")
        engagement_app = st.checkbox("Create entry in Engagement App", key="gtm_engagement")

        submitted = st.form_submit_button("Save Event")

        if submitted:
            if not (event_name and description and date and sa_id and topic and assignees):
                st.error("Please fill all mandatory fields")
            else:
                event_data = {
                    "name": event_name,
                    "description": description,
                    "id": f"gtm_onboarding_{datetime.now().timestamp()}",
                    "date": date.strftime("%Y-%m-%d"),
                    "sa_id": sa_id,
                    "topic": topic,
                    "useful_link": useful_link,
                    "assignees": ", ".join(assignees),
                    "travel_required": travel,
                    "engagement_app_entry": engagement_app,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "GTM Onboarding"):
                    st.rerun()

def form_blueprint_workshop():
    """Form for Blueprint Workshops."""
    st.subheader("Add Blueprint Workshop")

    with st.form("blueprint_form"):
        event_name = st.text_input("Event Name *", key="bp_name")
        description = st.text_area("Description *", height=100, key="bp_desc")
        workshop_name = st.selectbox("Workshop or Hackathon Type *", ["Workshop", "Hackathon"], key="bp_type")

        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From Date *", key="bp_from")
        with col2:
            to_date = st.date_input("To Date *", key="bp_to")

        platform = st.selectbox("Platform *", ["Blueprint", "1:1 CE Blueprint"], key="bp_platform")
        sa_id = st.text_input("SA ID *", key="bp_sa")

        st.write("**Assignees (Multi-select)**")
        assignees = st.multiselect("Select Assignees", TEAM_MEMBERS, key="bp_assignee")

        travel = st.checkbox("Travel Required", key="bp_travel")
        engagement_app = st.checkbox("Create entry in Engagement App", key="bp_engagement")

        submitted = st.form_submit_button("Save Event")

        if submitted:
            if not (event_name and description and workshop_name and from_date and to_date and platform and sa_id and assignees):
                st.error("Please fill all mandatory fields")
            else:
                event_data = {
                    "name": event_name,
                    "description": description,
                    "id": f"blueprint_{datetime.now().timestamp()}",
                    "workshop_type": workshop_name,
                    "from_date": from_date.strftime("%Y-%m-%d"),
                    "to_date": to_date.strftime("%Y-%m-%d"),
                    "platform": platform,
                    "sa_id": sa_id,
                    "assignees": ", ".join(assignees),
                    "travel_required": travel,
                    "engagement_app_entry": engagement_app,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "Blueprint Workshops"):
                    st.rerun()

def form_useful_links():
    """Form for Useful Links."""
    st.subheader("Add Useful Link")

    with st.form("useful_links_form"):
        title = st.text_input("Link Title *", key="useful_title")
        url = st.text_input("URL *", key="useful_url")
        category = st.text_input("Category", key="useful_category")

        submitted = st.form_submit_button("Save Link")

        if submitted:
            if not (title and url):
                st.error("Please fill all mandatory fields")
            else:
                event_data = {
                    "id": f"link_{datetime.now().timestamp()}",
                    "title": title,
                    "url": url,
                    "category": category,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if save_event_to_sheets(event_data, "Useful Links"):
                    st.rerun()

def view_events_list():
    """Display events in list view."""
    events_df = load_events()

    if events_df.empty:
        st.info("No events yet. Add one using the forms below!")
        return

    st.subheader("Events List")

    if not events_df.empty:
        event_types = events_df['event_type'].unique()
        selected_type = st.selectbox("Filter by Event Type", ["All"] + list(event_types))

        if selected_type != "All":
            filtered_df = events_df[events_df['event_type'] == selected_type]
        else:
            filtered_df = events_df

        for idx, row in filtered_df.iterrows():
            event_type = row.get('event_type', 'Unknown')
            event_name = row.get('name', 'Unnamed Event')[:100]
            emoji = EVENT_EMOJIS.get(event_type, "📌")

            with st.expander(f"{emoji} {event_name}..."):
                col1, col2 = st.columns([4, 1])

                with col1:
                    display_event_details(row, event_type)

                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        if delete_event_from_sheets(event_type, row.get('id', '')):
                            st.rerun()

def view_resource_schedule():
    """View all events for a selected team member with calendar."""
    st.subheader("Resource Schedule")

    selected_resource = st.selectbox("Select Team Member", TEAM_MEMBERS)

    if selected_resource:
        events_df = load_events()

        if events_df.empty:
            st.info("No events found.")
            return

        # Filter events where the resource is assigned
        resource_events = []

        for idx, event in events_df.iterrows():
            event_type = event.get('event_type', '')

            # Check assignees field
            if 'assignees' in event and event['assignees']:
                assignees_list = [a.strip() for a in str(event['assignees']).split(',')]
                if selected_resource in assignees_list:
                    resource_events.append(event)
                    continue

            # Check resource_name field (for PTOs)
            if 'resource_name' in event and event['resource_name'] == selected_resource:
                resource_events.append(event)
                continue

        if not resource_events:
            st.info(f"No events scheduled for {selected_resource}.")
            return

        # Sort by date
        resource_df = pd.DataFrame(resource_events)

        # Extract date field (either 'date' or 'from_date')
        def get_sort_date(row):
            if pd.notna(row.get('date')):
                try:
                    return pd.to_datetime(row['date'])
                except:
                    return pd.Timestamp.max
            elif pd.notna(row.get('from_date')):
                try:
                    return pd.to_datetime(row['from_date'])
                except:
                    return pd.Timestamp.max
            return pd.Timestamp.max

        resource_df['sort_date'] = resource_df.apply(get_sort_date, axis=1)
        resource_df = resource_df.sort_values('sort_date').reset_index(drop=True)

        st.write(f"**Total Events for {selected_resource}:** {len(resource_events)}")
        st.divider()

        # Calendar view for resource
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📅 Calendar View")
            now = datetime.now()
            cal_col1, cal_col2 = st.columns(2)
            with cal_col1:
                cal_year = st.number_input("Year", min_value=2024, max_value=2026, value=now.year, key="res_year")
            with cal_col2:
                cal_month = st.number_input("Month", min_value=1, max_value=12, value=now.month, key="res_month")

            # Render resource calendar
            month_calendar = cal.monthcalendar(cal_year, cal_month)
            month_name = cal.month_name[cal_month]

            st.markdown(f"**{month_name} {cal_year}**")

            # Days header
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            col_day = st.columns(7)
            for col, day in zip(col_day, days):
                col.markdown(f"<div style='text-align: center; font-weight: bold; border-bottom: 2px solid #0066cc; padding: 8px;'>{day}</div>", unsafe_allow_html=True)

            # Calendar grid
            for week in month_calendar:
                cols_week = st.columns(7)
                for col, day in zip(cols_week, week):
                    with col:
                        if day == 0:
                            st.markdown("<div style='height: 80px; border: 1px solid #ddd;'></div>", unsafe_allow_html=True)
                        else:
                            date_str = f"{cal_year}-{cal_month:02d}-{day:02d}"
                            day_events = get_events_for_date(date_str, resource_df)
                            event_count = len(day_events)

                            cell_bg = "#ffffff"
                            event_icons = ""
                            if not day_events.empty and event_count > 0:
                                cell_bg = EVENT_COLORS.get(day_events.iloc[0]['event_type'], "#ffffff")
                                for _, evt in day_events.iterrows():
                                    emoji = EVENT_EMOJIS.get(evt['event_type'], "📌")
                                    event_icons += emoji

                            button_text = f"{day}\n{event_icons}\n({event_count})"
                            col.button(button_text, key=f"res_date_{date_str}", use_container_width=True)

        with col2:
            st.subheader("📋 Event Details")
            st.write("Click events below for details")

        st.divider()

        # Display events grouped by date
        current_date = None
        for idx, event in resource_df.iterrows():
            event_type = event.get('event_type', 'Unknown')

            # Get the event date
            if pd.notna(event.get('date')):
                event_date = event['date']
            elif pd.notna(event.get('from_date')):
                if pd.notna(event.get('to_date')):
                    event_date = f"{event['from_date']} to {event['to_date']}"
                else:
                    event_date = event['from_date']
            else:
                event_date = "Unknown"

            # Date header
            if event_date != current_date:
                current_date = event_date
                st.subheader(f"📅 {event_date}")

            # Event card
            with st.expander(
                f"{EVENT_EMOJIS.get(event_type, '📌')} {event_type} - {event.get('name', 'Unnamed')}",
                expanded=False
            ):
                col1, col2 = st.columns(2)

                with col1:
                    if 'description' in event and event['description']:
                        st.write(f"**Description:** {event['description']}")

                    if event_type == "PTOs":
                        if 'leave_type' in event and event['leave_type']:
                            st.write(f"**Leave Type:** {event['leave_type']}")

                    elif event_type == "AI Assisted Agentic Development":
                        if 'sa_id' in event and event['sa_id']:
                            st.write(f"**SA ID:** {event['sa_id']}")
                        if 'pre_work_done' in event:
                            st.write(f"**Pre-work Done:** {event['pre_work_done']}")

                    elif event_type == "Lunch and Learns":
                        if 'topic' in event and event['topic']:
                            st.write(f"**Topic:** {event['topic']}")
                        if 'sa_id' in event and event['sa_id']:
                            st.write(f"**SA ID:** {event['sa_id']}")

                    elif event_type == "Hands on Experiences":
                        if 'sa_id' in event and event['sa_id']:
                            st.write(f"**SA ID:** {event['sa_id']}")
                        if 'itsm_ticket' in event and event['itsm_ticket']:
                            st.write(f"**ITSM Ticket:** {event['itsm_ticket']}")

                    elif event_type == "Blueprint Workshops":
                        if 'sa_id' in event and event['sa_id']:
                            st.write(f"**SA ID:** {event['sa_id']}")
                        if 'duration_hours' in event and event['duration_hours']:
                            st.write(f"**Duration:** {event['duration_hours']} hours")

                with col2:
                    if 'travel_required' in event and event['travel_required']:
                        st.warning(f"✈️ **Travel Required:** Yes")

                    if 'engagement_app_entry' in event and event['engagement_app_entry']:
                        st.success(f"📱 **Engagement App Entry:** Created")

                    if 'assignees' in event and event['assignees']:
                        st.write(f"**Team:** {event['assignees']}")

def view_reports(theme_colors=None):
    """View reports with resource allocation, event breakdown, and utilization."""
    if theme_colors is None:
        theme_colors = THEMES.get("Ocean Blue", {})

    st.subheader("📊 Reports & Analytics")

    now = datetime.now()
    col1, col2 = st.columns(2)
    with col1:
        report_year = st.number_input("Report Year", min_value=2024, max_value=2026, value=now.year)
    with col2:
        report_month = st.number_input("Report Month", min_value=1, max_value=12, value=now.month)

    events_df = load_events()

    if events_df.empty:
        st.info("No events to report.")
        return

    # Filter events for selected month
    month_events = []
    for idx, event in events_df.iterrows():
        event_date = None
        if 'date' in event and pd.notna(event['date']):
            try:
                event_date = pd.to_datetime(event['date'])
            except:
                pass
        elif 'from_date' in event and pd.notna(event['from_date']):
            try:
                event_date = pd.to_datetime(event['from_date'])
            except:
                pass

        if event_date and event_date.year == report_year and event_date.month == report_month:
            month_events.append(event)

    st.divider()

    # 1. Event Type Breakdown
    st.subheader("📈 Event Type Breakdown")
    if month_events:
        event_type_counts = {}
        for event in month_events:
            event_type = event.get('event_type', 'Unknown')
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        col1, col2 = st.columns([1.5, 1])
        with col1:
            import plotly.graph_objects as go

            colors_list = [EVENT_COLORS.get(et, "#808080") for et in event_type_counts.keys()]
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(event_type_counts.keys()),
                    values=list(event_type_counts.values()),
                    marker=dict(colors=colors_list)
                )
            ])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("**Count by Type:**")
            for event_type, count in sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True):
                emoji = EVENT_EMOJIS.get(event_type, "📌")
                st.metric(f"{emoji} {event_type}", count)
    else:
        st.info("No events in selected month.")

    st.divider()

    # 2. Resource Utilization
    st.subheader("👥 Resource Utilization")

    resource_events = {member: [] for member in TEAM_MEMBERS}
    for event in month_events:
        if 'assignees' in event and pd.notna(event['assignees']) and str(event['assignees']).strip():
            assignees_list = [a.strip() for a in str(event['assignees']).split(',') if a.strip()]
            for member in assignees_list:
                if member in resource_events:
                    resource_events[member].append(event)
        if 'resource_name' in event and pd.notna(event['resource_name']) and str(event['resource_name']).strip():
            resource_name = str(event['resource_name']).strip()
            if resource_name in resource_events:
                resource_events[resource_name].append(event)

    utilization_data = {member: len(events) for member, events in resource_events.items()}
    utilization_data = {k: v for k, v in sorted(utilization_data.items(), key=lambda x: x[1], reverse=True)}

    col1, col2 = st.columns([1.5, 1])
    with col1:
        import plotly.graph_objects as go
        fig = go.Figure(data=[
            go.Bar(
                x=list(utilization_data.keys()),
                y=list(utilization_data.values()),
                marker_color=theme_colors.get('primary', '#0066cc')
            )
        ])
        fig.update_layout(
            title="Events per Team Member",
            xaxis_title="Team Member",
            yaxis_title="Number of Events",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("**Team Member Load:**")
        for member, count in utilization_data.items():
            if count > 0:
                st.write(f"• {member}: {count} events")
        if all(v == 0 for v in utilization_data.values()):
            st.info("No team members assigned to events this month.")

    st.divider()

    # 3. Resource Allocation Calendar
    st.subheader("📅 Resource Allocation by Date")

    # Color legend for calendar
    st.markdown("**Color Legend:**")
    legend_cols = st.columns(5)

    event_types_legend = [
        ("🎓 Hands on", EVENT_COLORS["Hands on Experiences"]),
        ("📴 Leaves", EVENT_COLORS["Leaves"]),
        ("🤖 AI Agentic", EVENT_COLORS["AI Assisted Agentic Development"]),
        ("🥗 Lunch & Learn", EVENT_COLORS["Lunch and Learns"]),
        ("🎪 Workshops", EVENT_COLORS["Blueprint Workshops"]),
        ("🚀 GTM Onboarding", EVENT_COLORS["GTM Onboarding"])
    ]

    for col, (label, color) in zip(legend_cols, event_types_legend):
        with col:
            st.markdown(f"""
            <div style='background-color: {color}; border: 2px solid #333; border-radius: 5px; padding: 10px; text-align: center; font-weight: bold; font-size: 12px;'>
                {label}
            </div>
            """, unsafe_allow_html=True)

    month_calendar = cal.monthcalendar(report_year, report_month)
    month_name = cal.month_name[report_month]

    calendar_bg = theme_colors.get("calendar_bg", "#e6f2ff")
    calendar_border = theme_colors.get("calendar_border", "#0066cc")

    st.markdown(f"""
    <style>
    .allocation-calendar {{
        background-color: {calendar_bg};
        border: 3px solid {calendar_border};
        border-radius: 8px;
        padding: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for col, day in zip(cols, days):
        with col:
            st.markdown(f"<div style='text-align: center; font-weight: bold; border-bottom: 2px solid {calendar_border}; padding: 10px;'>{day}</div>", unsafe_allow_html=True)

    for week in month_calendar:
        cols = st.columns(7)
        for col, day in zip(cols, week):
            with col:
                if day == 0:
                    st.markdown("<div style='height: 120px; border: 1px solid #ddd;'></div>", unsafe_allow_html=True)
                else:
                    date_str = f"{report_year}-{report_month:02d}-{day:02d}"
                    day_events = get_events_for_date(date_str, pd.DataFrame(month_events))

                    # Collect assignees for this day
                    day_assignees = set()
                    for _, event in day_events.iterrows():
                        if 'assignees' in event and pd.notna(event['assignees']) and str(event['assignees']).strip():
                            assignees_list = [a.strip() for a in str(event['assignees']).split(',') if a.strip()]
                            day_assignees.update(assignees_list)
                        if 'resource_name' in event and pd.notna(event['resource_name']) and str(event['resource_name']).strip():
                            day_assignees.add(str(event['resource_name']).strip())

                    # Filter out empty strings and convert to list for sorting
                    day_assignees = [str(a) for a in day_assignees if a]
                    assignee_text = "<br>".join(sorted(day_assignees)[:3])  # Show top 3
                    if len(day_assignees) > 3:
                        assignee_text += f"<br>+{len(day_assignees)-3} more"

                    cell_bg = "#ffffff"
                    if day_assignees:
                        cell_bg = EVENT_COLORS.get(day_events.iloc[0]['event_type'], "#ffffff")

                    # Determine text color based on background brightness
                    text_color = "#000" if cell_bg == "#ffffff" else "#fff"
                    st.markdown(f"""
                    <div style='border: 1px solid {calendar_border}; background-color: {cell_bg}; padding: 8px; min-height: 120px; font-size: 12px; color: {text_color}; border-radius: 4px;'>
                        <b style='color: {text_color};'>{day}</b>
                        <div style='margin-top: 5px; color: {text_color}; text-shadow: 0 1px 2px rgba(0,0,0,0.2);'>{assignee_text if assignee_text else "-"}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.divider()

    # 4. Events by Month (Excluding Leaves)
    st.subheader("📅 Events by Month")

    import plotly.graph_objects as go

    # Get all events for the year, excluding leaves
    year_events = []
    for idx, event in events_df.iterrows():
        if event.get('event_type') == 'Leaves':
            continue
        event_date = None
        if 'date' in event and pd.notna(event['date']):
            try:
                event_date = pd.to_datetime(event['date'])
            except:
                pass
        elif 'from_date' in event and pd.notna(event['from_date']):
            try:
                event_date = pd.to_datetime(event['from_date'])
            except:
                pass

        if event_date and event_date.year == report_year:
            year_events.append(event)

    # Count events by month and event type
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_by_type = {}

    for event in year_events:
        event_type = event.get('event_type', 'Unknown')
        event_date = None
        if 'date' in event and pd.notna(event['date']):
            try:
                event_date = pd.to_datetime(event['date'])
            except:
                pass
        elif 'from_date' in event and pd.notna(event['from_date']):
            try:
                event_date = pd.to_datetime(event['from_date'])
            except:
                pass
        if event_date:
            month = event_date.month
            if month not in monthly_by_type:
                monthly_by_type[month] = {}
            monthly_by_type[month][event_type] = monthly_by_type[month].get(event_type, 0) + 1

    # Get all event types
    all_event_types = sorted(set(e.get('event_type', 'Unknown') for e in year_events))

    # Create stacked bar chart
    fig_month = go.Figure()

    for event_type in all_event_types:
        values = [monthly_by_type.get(month, {}).get(event_type, 0) for month in range(1, 13)]
        fig_month.add_trace(go.Bar(
            x=month_names,
            y=values,
            name=event_type,
            marker_color=EVENT_COLORS.get(event_type, "#808080")
        ))

    fig_month.update_layout(
        title=f"Events by Month - {report_year} (By Type)",
        xaxis_title="Month",
        yaxis_title="Number of Events",
        barmode='stack',
        height=400
    )
    st.plotly_chart(fig_month, use_container_width=True)

    # CSV export for monthly data
    col1, col2 = st.columns([3, 1])
    with col2:
        monthly_export = {"Month": month_names}
        for event_type in all_event_types:
            monthly_export[event_type] = [monthly_by_type.get(month, {}).get(event_type, 0) for month in range(1, 13)]

        monthly_df = pd.DataFrame(monthly_export)
        csv_monthly = monthly_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Monthly CSV",
            data=csv_monthly,
            file_name=f"events_by_month_{report_year}.csv",
            mime="text/csv"
        )

    st.divider()

    # 5. Events by Quarter (Excluding Leaves)
    st.subheader("📊 Events by Quarter")

    # Count events by quarter and event type
    quarterly_by_type = {}
    for event in year_events:
        event_type = event.get('event_type', 'Unknown')
        event_date = None
        if 'date' in event and pd.notna(event['date']):
            try:
                event_date = pd.to_datetime(event['date'])
            except:
                pass
        elif 'from_date' in event and pd.notna(event['from_date']):
            try:
                event_date = pd.to_datetime(event['from_date'])
            except:
                pass
        if event_date:
            quarter = (event_date.month - 1) // 3 + 1
            if quarter not in quarterly_by_type:
                quarterly_by_type[quarter] = {}
            quarterly_by_type[quarter][event_type] = quarterly_by_type[quarter].get(event_type, 0) + 1

    quarters = ["Q1", "Q2", "Q3", "Q4"]

    # Create stacked bar chart for quarters
    fig_quarter = go.Figure()

    for event_type in all_event_types:
        values = [quarterly_by_type.get(q, {}).get(event_type, 0) for q in range(1, 5)]
        fig_quarter.add_trace(go.Bar(
            x=quarters,
            y=values,
            name=event_type,
            marker_color=EVENT_COLORS.get(event_type, "#808080")
        ))

    fig_quarter.update_layout(
        title=f"Events by Quarter - {report_year} (By Type)",
        xaxis_title="Quarter",
        yaxis_title="Number of Events",
        barmode='stack',
        height=400
    )
    st.plotly_chart(fig_quarter, use_container_width=True)

    # CSV export for quarterly data
    col1, col2 = st.columns([3, 1])
    with col2:
        quarterly_export = {"Quarter": quarters}
        for event_type in all_event_types:
            quarterly_export[event_type] = [quarterly_by_type.get(q, {}).get(event_type, 0) for q in range(1, 5)]

        quarterly_df = pd.DataFrame(quarterly_export)
        csv_quarterly = quarterly_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Quarterly CSV",
            data=csv_quarterly,
            file_name=f"events_by_quarter_{report_year}.csv",
            mime="text/csv"
        )

def export_events_to_csv(events_df, filename="events.csv"):
    """Convert events dataframe to CSV string."""
    if events_df.empty:
        return None
    
    csv_buffer = StringIO()
    events_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def show_export_sidebar():
    """Show export options in sidebar."""
    with st.sidebar:
        st.header("📥 Export Data")
        st.markdown("---")
        
        export_option = st.selectbox(
            "Select Export Type",
            [
                "All Events",
                "By Event Type",
                "By Team Member",
                "By Date Range",
                "Useful Links"
            ]
        )
        
        events_df = load_events()
        export_data = None
        filename = "events.csv"
        
        if export_option == "All Events":
            if not events_df.empty:
                export_data = export_events_to_csv(events_df, "all_events.csv")
                filename = f"all_events_{datetime.now().strftime('%Y%m%d')}.csv"
                if st.button("📥 Download All Events"):
                    st.download_button(
                        label="Click to Download",
                        data=export_data,
                        file_name=filename,
                        mime="text/csv"
                    )
        
        elif export_option == "By Event Type":
            event_type = st.selectbox("Select Event Type", list(EVENT_TYPES.keys())[:-1])
            filtered_df = events_df[events_df['event_type'] == event_type] if not events_df.empty else pd.DataFrame()
            
            if not filtered_df.empty:
                export_data = export_events_to_csv(filtered_df)
                filename = f"{event_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
                if st.button(f"📥 Download {event_type}"):
                    st.download_button(
                        label="Click to Download",
                        data=export_data,
                        file_name=filename,
                        mime="text/csv"
                    )
            else:
                st.info(f"No {event_type} events to export.")
        
        elif export_option == "By Team Member":
            team_member = st.selectbox("Select Team Member", TEAM_MEMBERS)
            
            member_events = []
            for idx, event in events_df.iterrows():
                if 'assignees' in event and event['assignees']:
                    assignees_list = [a.strip() for a in str(event['assignees']).split(',')]
                    if team_member in assignees_list:
                        member_events.append(event)
                if 'resource_name' in event and event['resource_name'] == team_member:
                    member_events.append(event)
            
            if member_events:
                member_df = pd.DataFrame(member_events)
                export_data = export_events_to_csv(member_df)
                filename = f"{team_member.replace(' ', '_')}_events_{datetime.now().strftime('%Y%m%d')}.csv"
                if st.button(f"📥 Download {team_member} Events"):
                    st.download_button(
                        label="Click to Download",
                        data=export_data,
                        file_name=filename,
                        mime="text/csv"
                    )
            else:
                st.info(f"No events for {team_member}.")
        
        elif export_option == "By Date Range":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", key="export_start")
            with col2:
                end_date = st.date_input("End Date", key="export_end")
            
            if start_date <= end_date:
                range_events = []
                for idx, event in events_df.iterrows():
                    event_date = None
                    if 'date' in event and pd.notna(event['date']):
                        try:
                            event_date = pd.to_datetime(event['date'])
                        except:
                            pass
                    elif 'from_date' in event and pd.notna(event['from_date']):
                        try:
                            event_date = pd.to_datetime(event['from_date'])
                        except:
                            pass
                    
                    if event_date and start_date <= event_date.date() <= end_date:
                        range_events.append(event)
                
                if range_events:
                    range_df = pd.DataFrame(range_events)
                    export_data = export_events_to_csv(range_df)
                    filename = f"events_{start_date}_{end_date}_{datetime.now().strftime('%Y%m%d')}.csv"
                    if st.button("📥 Download Date Range Events"):
                        st.download_button(
                            label="Click to Download",
                            data=export_data,
                            file_name=filename,
                            mime="text/csv"
                        )
                else:
                    st.info("No events in selected date range.")
        
        elif export_option == "Useful Links":
            links_df = load_useful_links()
            if not links_df.empty:
                export_data = export_events_to_csv(links_df)
                filename = f"useful_links_{datetime.now().strftime('%Y%m%d')}.csv"
                if st.button("📥 Download Useful Links"):
                    st.download_button(
                        label="Click to Download",
                        data=export_data,
                        file_name=filename,
                        mime="text/csv"
                    )
            else:
                st.info("No useful links to export.")


def clear_all_data():
    """Clear all event data from Google Sheets."""
    client = get_google_sheets_client()
    if not client:
        st.error("Cannot connect to Google Sheets")
        return False

    try:
        sheet_id = st.secrets["GOOGLE_SHEETS_ID"]
        spreadsheet = client.open_by_key(sheet_id)

        # List of worksheets to clear (excluding Useful Links for now)
        worksheets_to_clear = [
            "Hands on Experiences",
            "Leaves",
            "AI Assisted Agentic Development",
            "Lunch and Learns",
            "Blueprint Workshops",
            "GTM Onboarding"
        ]

        for ws_name in worksheets_to_clear:
            try:
                worksheet = spreadsheet.worksheet(ws_name)
                # Get all values
                all_values = worksheet.get_all_values()
                # If there are rows beyond the header, delete them
                if len(all_values) > 1:
                    worksheet.delete_rows(2, len(all_values))
            except:
                pass

        st.session_state.success_message = "✅ All data has been cleared successfully!"
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error clearing data: {str(e)}")
        return False


def main():
    st.set_page_config(page_title="APJ DemoX Events Tracker", layout="wide", initial_sidebar_state="expanded")

    # Theme selector in sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        selected_theme = st.selectbox(
            "Choose Theme",
            list(THEMES.keys()),
            index=0
        )
        theme_colors = THEMES[selected_theme]

        # Apply theme to page with button styling
        st.markdown(f"""
        <style>
        :root {{
            --primary-color: {theme_colors['primary']};
        }}

        /* Style primary buttons with theme color */
        div.stButton > button {{
            background-color: {theme_colors['primary']} !important;
            color: white !important;
            border-color: {theme_colors['accent']} !important;
        }}

        div.stButton > button:hover {{
            background-color: {theme_colors['accent']} !important;
            border-color: {theme_colors['primary']} !important;
        }}

        /* Style selectbox with theme color */
        .stSelectbox [data-baseweb="select"] {{
            border-color: {theme_colors['primary']} !important;
        }}

        /* Style radio buttons with theme color */
        [data-testid="stRadio"] label {{
            color: {theme_colors['primary']} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

    # Show export sidebar
    show_export_sidebar()

    # Add clear data section
    with st.sidebar:
        st.markdown("---")
        st.header("🗑️ Data Management")

        # Initialize session state for clear confirmation
        if 'show_clear_confirmation' not in st.session_state:
            st.session_state.show_clear_confirmation = False

        if st.session_state.show_clear_confirmation:
            st.warning("⚠️ Are you sure? This will delete all event data!")
            password = st.text_input("Enter password to confirm:", type="password", key="clear_password")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Clear", use_container_width=True, key="confirm_clear"):
                    if password == "RulesDemoXAPJ":
                        clear_all_data()
                        st.session_state.show_clear_confirmation = False
                        st.session_state.clear_password = ""
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password")
            with col2:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_clear"):
                    st.session_state.show_clear_confirmation = False
                    st.session_state.clear_password = ""
                    st.rerun()
        else:
            if st.button("🗑️ Clear All Data", use_container_width=True):
                st.session_state.show_clear_confirmation = True
                st.rerun()

    if 'success_message' in st.session_state and st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    st.title("📅 APJ DemoX Events Tracker")
    st.markdown("*Manage hands-on experiences, PTOs, training sessions, and more*")

    view_mode = st.radio("View", ["Calendar & List", "Add Event", "Resource Schedule", "Reports", "Useful Links"], horizontal=True)

    if view_mode == "Calendar & List":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Month View (Click date to see events)")
            now = datetime.now()
            col_year, col_month = st.columns(2)
            with col_year:
                year = st.number_input("Year", min_value=2024, max_value=2026, value=now.year)
            with col_month:
                month = st.number_input("Month", min_value=1, max_value=12, value=now.month)

            render_calendar_month(year, month, theme_colors)

        with col2:
            st.subheader("Navigation")
            if st.button("Today"):
                st.session_state.selected_date = None
                st.rerun()

        st.divider()
        
        if 'selected_date' in st.session_state and st.session_state.selected_date:
            events_df = load_events()
            show_events_for_date(st.session_state.selected_date, events_df)
        else:
            view_events_list()

    elif view_mode == "Add Event":
        event_type = st.selectbox(
            "Select Event Type",
            list(EVENT_TYPES.keys())
        )

        st.divider()

        if event_type == "Hands on Experiences":
            form_hands_on_experiences()
        elif event_type == "Leaves":
            form_pto()
        elif event_type == "AI Assisted Agentic Development":
            form_ai_agentic()
        elif event_type == "Lunch and Learns":
            form_lunch_learn()
        elif event_type == "Blueprint Workshops":
            form_blueprint_workshop()
        elif event_type == "GTM Onboarding":
            form_gtm_onboarding()

    elif view_mode == "Resource Schedule":
        view_resource_schedule()

    elif view_mode == "Reports":
        view_reports(theme_colors)

    elif view_mode == "Useful Links":
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Useful Links")
            links_df = load_useful_links()

            if not links_df.empty:
                for idx, link in links_df.iterrows():
                    title = link.get('title', 'Untitled Link')
                    url = link.get('url', '#')
                    category = link.get('category', '')

                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div style='margin: 15px 0;'>
                            <a href='{url}' target='_blank' style='font-size: 18px; font-weight: 600; color: #0066cc; text-decoration: none; line-height: 1.4;'>{title}</a>
                            {f"<div style='font-size: 13px; color: #666; margin-top: 6px;'>📁 {category}</div>" if category else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("🗑️", key=f"delete_link_{idx}"):
                            delete_event_from_sheets("Useful Links", link.get('id', ''))
                            st.rerun()
                    st.divider()
            else:
                st.info("No useful links yet.")

        with col2:
            st.subheader("Add Link")
            form_useful_links()

if __name__ == "__main__":
    main()
