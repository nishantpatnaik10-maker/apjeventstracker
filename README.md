# 📅 APJ DemoX Events Tracker

A Streamlit-based event management system for tracking hands-on experiences, leaves, training sessions, workshops, and more across the APJ region. Built with Python, Streamlit, and Google Sheets for real-time data synchronization.

**Live Demo**: https://demoxapjevents.streamlit.app/

---

## ✨ Features

- **📅 Interactive Calendar** - Month view with color-coded events and emoji indicators
- **📋 Event Management** - Add, edit, and delete events with event-specific validation
- **6 Event Types**:
  - 🎓 Hands on Experiences
  - 📴 Leaves (with multi-day support and date validation)
  - 🤖 AI Assisted Agentic Development
  - 🥗 Lunch and Learns
  - 🎪 Blueprint Workshops
  - 🚀 GTM Onboarding
- **👥 Team Assignment** - Multi-select assignee field for team members
- **📊 Reports & Analytics** - Event breakdown, resource utilization charts, resource allocation calendar
- **🔗 Resource Schedule** - Calendar view of team member assignments
- **📥 CSV Export** - Download events with custom filtering
- **🎨 Customizable Themes** - 5 built-in color themes (Ocean Blue, Forest Green, Sunset Orange, Purple Royale, Modern Slate)
- **🔐 Password-Protected Operations** - Clear data functionality requires password
- **☁️ Google Sheets Sync** - Real-time data persistence and backup
- **🌐 Cloud Deployment** - Hosted on Streamlit Cloud for easy access

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your machine
- **Git** for cloning the repository
- **Google Account** with access to Google Cloud Console
- **GitHub Account** (for deployment to Streamlit Cloud)

---

## 🚀 Quick Start

### Option 1: Use the Live App (No Setup Required)
Simply visit: https://demoxapjevents.streamlit.app/

### Option 2: Run Locally

#### 1. Clone the Repository
```bash
git clone https://github.com/nishantpatnaik10-maker/apjeventstracker.git
cd apjeventstracker
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Up Google Cloud Credentials (See Section Below)

#### 4. Create Local Credentials File
Create a file named `credentials.json` in the project root with your Google service account credentials.

#### 5. Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🔐 Google Cloud Setup

Follow these steps to set up Google Sheets integration:

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** at the top
3. Enter project name: `apj-demox-events`
4. Click **Create**
5. Wait for the project to be created and select it

### Step 2: Enable Google Sheets API
1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for **"Google Sheets API"**
3. Click on it and press **Enable**

### Step 3: Create a Service Account
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in the details:
   - Service account name: `demox-events-tracker`
   - Click **Create and Continue**
4. Skip optional steps and click **Done**

### Step 4: Create and Download Key
1. In Credentials, click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** format
5. Click **Create** - a file will be downloaded automatically
6. Save this as `credentials.json` in your project folder

### Step 5: Share Google Sheet with Service Account
1. Get the **client_email** from `credentials.json` (looks like `demox-events-tracker@apj-demox-events.iam.gserviceaccount.com`)
2. Go to your [Google Sheet](https://docs.google.com/spreadsheets/d/1wpJSSYoHKKtzVN1e4X4b9pnrTNkVM0rMGBJubGh6xhk)
3. Click **Share** button
4. Add the service account email and give **Editor** access
5. Click **Share**

---

## 📱 Deployment to Streamlit Cloud

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository: `apjeventstracker`
4. Select branch: `main`
5. Set main file path: `app.py`
6. Click **Deploy**

### Step 3: Configure Secrets
Once deployed:
1. Click the **⋮** menu (top right) → **Settings**
2. Go to **Secrets** tab
3. Add your credentials in TOML format:

```toml
GOOGLE_SHEETS_ID = "1wpJSSYoHKKtzVN1e4X4b9pnrTNkVM0rMGBJubGh6xhk"

GOOGLE_SERVICE_ACCOUNT_JSON_STR = '{"type": "service_account", "project_id": "apj-demox-events", "private_key_id": "YOUR_KEY_ID", "private_key": "YOUR_PRIVATE_KEY", "client_email": "YOUR_EMAIL", "client_id": "YOUR_CLIENT_ID", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "YOUR_CERT_URL"}'
```

4. Click **Save**
5. Wait 1-2 minutes for redeploy

**Note**: Copy the entire `credentials.json` content and paste it as a single JSON string for `GOOGLE_SERVICE_ACCOUNT_JSON_STR`.

---

## 📊 Event Types & Fields

### Hands on Experiences 🎓
- **Event Name** * (mandatory)
- **Description** * (mandatory)
- **Date** * (mandatory)
- **SA ID** * (mandatory)
- **Assignees** * (multi-select)
- **Create entry in Engagement App** (checkbox)

### Leaves 📴
- **Resource Name** * (dropdown)
- **Description** * (mandatory)
- **From Date** * (mandatory)
- **To Date** * (mandatory, must be after From Date)
- **Type of Leave** * (Sick, Personal, Carers, Bereavement, Maternity, Paternity)
- ⚠️ **Validation**: To Date must be after From Date

### AI Assisted Agentic Development 🤖
- **Event Name** * (mandatory)
- **Description** * (mandatory)
- **Date** * (mandatory)
- **SA ID** * (mandatory)
- **Pre work done** * (checkbox)
- **Assignees** * (multi-select)
- **Travel Required** (checkbox)
- **Create entry in Engagement App** (checkbox)

### Lunch and Learns 🥗
- **Event Name** * (mandatory)
- **Description** * (mandatory)
- **Date** * (mandatory)
- **SA ID** * (mandatory)
- **Topic** * (mandatory)
- **Useful links** (optional)
- **Assignees** * (multi-select)
- **Travel Required** (checkbox)
- **Create entry in Engagement App** (checkbox)

### Blueprint Workshops 🎪
- **Event Name** * (mandatory)
- **Description** * (mandatory)
- **Date** * (mandatory)
- **Workshop Type** * (dropdown: Workshop or Hackathon)
- **SA ID** * (mandatory)
- **Assignees** * (multi-select)
- **Create entry in Engagement App** (checkbox)

### GTM Onboarding 🚀
- **Event Name** * (mandatory)
- **Description** * (mandatory)
- **Date** * (mandatory)
- **SA ID** * (mandatory)
- **Topic** * (mandatory)
- **Useful links** (optional)
- **Assignees** * (multi-select)
- **Travel Required** (checkbox)
- **Create entry in Engagement App** (checkbox)

---

## 🔒 Security & Passwords

### Clear Data Protection
The "Clear All Data" function is password-protected:
- **Password**: `RulesDemoXAPJ`
- Prevents accidental deletion of all events
- Only authorized operators can clear the database

### Credential Security
- `credentials.json` is in `.gitignore` (never committed to GitHub)
- On Streamlit Cloud, credentials are stored as encrypted secrets
- Each deployment can have different credentials for different environments

---

## 📁 Project Structure

```
apjeventstracker/
├── app.py                      # Main application
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml.example   # Template for secrets (local only)
├── credentials.json           # Google service account (local only)
├── README.md                  # This file
└── .github/
    └── workflows/             # GitHub Actions (if configured)
```

---

## 🛠️ Local Development

### Install Development Dependencies
```bash
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run app.py
```

### Code Structure
- **app.py**: Main Streamlit application (~1400 lines)
  - Event type forms
  - Calendar rendering
  - Reports and analytics
  - Google Sheets integration
  - Data management

### Modifying the Code
1. Edit `app.py`
2. Streamlit automatically reloads on save
3. Test in browser at `http://localhost:8501`
4. Commit and push to GitHub to deploy to cloud

---

## 🐛 Troubleshooting

### "Error connecting to Google Sheets: Unable to load PEM file"
**Solution**: 
- Ensure `credentials.json` exists in project root
- Check the JSON is valid (no escaped characters)
- For Streamlit Cloud, verify secrets are in TOML format

### "Error: Unable to find worksheet"
**Solution**:
- Worksheets are created automatically on first event save
- Ensure service account has Editor access to the Google Sheet
- Try adding a new event to create the worksheet

### Events not appearing on calendar
**Solution**:
- Verify the Google Sheet has proper headers
- Check that dates are formatted as YYYY-MM-DD
- Clear browser cache and refresh (Cmd+Shift+R / Ctrl+Shift+R)

### Password protection not working on clear data
**Solution**:
- Ensure you entered the correct password: `RulesDemoXAPJ`
- Check for typos (case-sensitive)
- Refresh the browser if button seems unresponsive

### Icons not displaying correctly
**Solution**:
- Hard refresh browser cache
- Clear Streamlit cache: Delete `.streamlit/cache` folder locally

---

## 🤝 Contributing

To contribute to this project:

1. **Fork the repository** on GitHub
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test locally
4. **Commit with descriptive messages**:
   ```bash
   git commit -m "Add feature: description"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** with a description of changes

---

## 📞 Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review [GitHub Issues](https://github.com/nishantpatnaik10-maker/apjeventstracker/issues)
3. Contact the development team

---

## 📄 License

Internal use only - APJ DemoX team

---

## 🔄 Recent Updates

- ✅ Fixed Google Sheets column alignment
- ✅ Added date validation for Leaves (To Date must be after From Date)
- ✅ Added password protection for Clear Data function
- ✅ Updated emoji icons for all event types
- ✅ Added support for JSON string format credentials
- ✅ Implemented consistent column ordering in Google Sheets
- ✅ Added cache clearing for proper icon rendering

---

**Questions?** Contact the development team or create an issue on GitHub.
