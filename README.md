# 📅 APJ DemoX Events Tracker

A Streamlit-based event management system for tracking hands-on experiences, PTOs, training sessions, workshops, and useful links across the APJ team.

## Features

- 📅 **Month View Calendar** - Visual representation of events throughout the month
- 📋 **List View** - Detailed view of all events with filtering
- ✅ **Multiple Event Types**:
  - Hands on Experiences
  - PTOs (Sick, Personal, Carers, Bereavement, Maternity, Paternity)
  - AI Assisted Agentic Development Experience sessions
  - Lunch and Learns
  - Blueprint Workshops
- 👥 **Team Member Assignment** - Assign events to team members with specific roles (Lead, Emcee, Facilitator, Moderator, Support)
- 🔗 **Useful Links** - Store and organize helpful resources
- ☁️ **Google Sheets Integration** - All data synced to Google Sheets for easy export and sharing
- 🌐 **Public Access** - Accessible via public URL when deployed to Streamlit Cloud

## Event Types & Required Fields

### Hands on Experiences
- From Date * (Mandatory)
- To Date * (Mandatory)
- Location * (Mandatory)
- Experiences * (Mandatory) - Customer service, Back Office, Infinity Studio, Agentic, CDH/BP, Blueprint legacy transformation experience
- SA ID (Optional)
- ITSM Ticket Number * (Mandatory)
- Number of assets required (Optional)
- Assignee with Role and Travel Required flag

### PTOs
- From Date * (Mandatory)
- To Date * (Mandatory)
- Type of Leave * (Mandatory) - Sick, Personal, Carers, Bereavement, Maternity, Paternity

### AI Assisted Agentic Development Experience
- Date * (Mandatory)
- SA ID * (Mandatory)
- Pre work done * (Mandatory)

### Lunch and Learns
- Date * (Mandatory)
- SA ID * (Mandatory)
- Topic * (Mandatory)
- Useful links (Optional)

### Blueprint Workshops
- Workshop or Hackathon Name * (Mandatory)
- From Date * (Mandatory)
- To Date * (Mandatory)
- Platform * (Mandatory) - Blueprint or 1:1 CE Blueprint
- SA ID * (Mandatory)
- Assignee with Role and Travel Required flag

### Useful Links
- Title * (Mandatory)
- URL * (Mandatory)
- Category (Optional)

## Team Members
- John Bai
- Katherine Chen
- Yianni Mannias
- Masashi Tsuneizumi
- Ankit Sharma
- Nishant Patnaik

## Quick Start

### 1. Google Cloud Setup
See **GOOGLE_CLOUD_SETUP.md** for detailed instructions on:
- Creating a Google Cloud Project
- Enabling Google Sheets API
- Creating a Service Account
- Downloading credentials

### 2. Configure Credentials
See **CREDENTIALS_CONFIG.md** for:
- How to set up `.streamlit/secrets.toml`
- Configuring local development
- Deploying to Streamlit Cloud

### 3. Local Development
```bash
cd events-tracker
pip install -r requirements.txt
streamlit run app.py
```

### 4. Deploy to Streamlit Cloud
- Push code to GitHub
- Deploy via https://share.streamlit.io
- Add secrets in cloud dashboard

## Documentation

- **QUICKSTART_CHECKLIST.md** - Step-by-step checklist to follow
- **GOOGLE_CLOUD_SETUP.md** - Detailed Google Cloud configuration
- **CREDENTIALS_CONFIG.md** - Credentials setup and troubleshooting
- **SETUP_GUIDE.md** - Complete setup and deployment instructions

## Troubleshooting

### "Error connecting to Google Sheets"
- Verify `GOOGLE_SHEETS_ID` is correct
- Check `.streamlit/secrets.toml` exists
- Ensure service account email has access to the sheet

### Events not saving
- Check Google Service Account has "Editor" access to the sheet
- Verify JSON credentials are properly formatted
- Look at Streamlit console for detailed error messages

## License

Internal use only - APJ DemoX team
