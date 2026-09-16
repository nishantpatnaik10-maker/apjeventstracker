# APJ DemoX Events Calendar - Deployment Guide

The Events Calendar is a Flask-based web application that displays events from Google Sheets with an interactive calendar interface.

## Local Setup

### Prerequisites
- Python 3.8+
- Google Sheets with events data
- Google Service Account credentials (credentials.json)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up credentials:**
   - Place `credentials.json` in the project root (or use environment variables)

3. **Run locally:**
```bash
python3 calendar_server.py
```

4. **Access the calendar:**
   - Open http://localhost:5000 in your browser

## Deployment Options

### Option 1: Deploy to Render (Recommended)

Render is a free/cheap hosting platform that works well for Flask apps.

1. **Push to GitHub** (see below)

2. **Create a new Web Service on Render:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Build command: `pip install -r requirements.txt`
   - Start command: `python3 calendar_server.py`

3. **Set Environment Variables:**
   - Add `GOOGLE_SHEETS_ID` with your Google Sheets ID
   - Create and upload `credentials.json` or store credentials as JSON in environment variables

4. **Deploy:**
   - Click "Create Web Service"
   - Your app will be live at `https://your-app-name.onrender.com`

### Option 2: Deploy to Railway

1. **Connect GitHub account to Railway** at https://railway.app

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add variables in Railway dashboard:**
   - `GOOGLE_SHEETS_ID`
   - Upload credentials.json file

4. **Deploy:**
   - Railway auto-deploys on every push
   - Get your live URL from the Railway dashboard

### Option 3: Deploy to Heroku

1. **Install Heroku CLI**

2. **Create Procfile:**
```
web: python3 calendar_server.py
```

3. **Deploy:**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Option 4: Deploy to Your Own Server

1. **On your server, install:**
   - Python 3.8+
   - pip
   - Git

2. **Clone repository:**
```bash
git clone https://github.com/nishantpatnaik10-maker/apjeventstracker.git
cd apjeventstracker
```

3. **Install and run:**
```bash
pip install -r requirements.txt
python3 calendar_server.py
```

4. **Use a production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 calendar_server:app
```

5. **Use a reverse proxy (nginx/Apache) to serve your app**

## Features

✅ Interactive calendar view  
✅ Event filtering (excludes Leaves automatically)  
✅ Click events to see details:
- Event name & type
- Date (formatted)
- Full description
- Engagement status
- SA ID
- Assignees

✅ Month navigation  
✅ Color-coded event types  
✅ Responsive design (mobile-friendly)  
✅ Real-time data from Google Sheets  

## Environment Variables

If using environment variables instead of credentials.json:

```
GOOGLE_SHEETS_ID=your-sheet-id
```

The app will automatically load credentials from:
1. Streamlit secrets (st.secrets) if available
2. `credentials.json` file in the project root

## Troubleshooting

**Error: "credentials.json not found"**
- Ensure credentials.json is in the project root
- Or set up credentials via environment variables in your deployment platform

**Error: "Google Sheets API not enabled"**
- Go to Google Cloud Console
- Enable "Google Sheets API" for your project

**Events not loading**
- Verify your Google Sheets ID is correct
- Check that the service account has access to the spreadsheet
- Ensure worksheets are named correctly (Hands on Experiences, AI Assisted Agentic Development, etc.)

## Security Notes

- **Never commit credentials.json to GitHub** (it's in .gitignore)
- Use environment variables in production
- Keep your service account credentials secure
- Only share the live calendar URL, not your Google Sheets directly

## URLs

- **Local:** http://localhost:5000
- **Production:** Check your deployment platform dashboard for the live URL

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the GitHub repository README
3. Check logs on your deployment platform
