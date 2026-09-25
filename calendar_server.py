#!/usr/bin/env python3
"""
Flask server for APJ DemoX Events Calendar
Fetches events from Google Sheets and serves interactive calendar
"""

from flask import Flask, render_template_string, jsonify
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# Google Sheets credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_google_sheets_client():
    """Initialize Google Sheets client."""
    creds_dict = None

    # Try environment variable first (for cloud deployments)
    if os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_STR'):
        try:
            creds_dict = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_STR'))
            print("✓ Loaded credentials from GOOGLE_SERVICE_ACCOUNT_JSON_STR")
        except Exception as e:
            print(f"Error parsing GOOGLE_SERVICE_ACCOUNT_JSON_STR: {e}")

    # Try Render secret file path
    if not creds_dict:
        try:
            with open('/etc/render/credentials.json') as f:
                creds_dict = json.load(f)
                print("✓ Loaded credentials from /etc/render/credentials.json")
        except:
            pass

    # Try Streamlit secrets (if running in Streamlit environment)
    if not creds_dict:
        try:
            import streamlit as st
            if "GOOGLE_SERVICE_ACCOUNT_JSON" in st.secrets:
                creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
                print("✓ Loaded credentials from Streamlit secrets")
        except:
            pass

    # Fall back to local credentials.json file
    if not creds_dict:
        try:
            with open('credentials.json') as f:
                creds_dict = json.load(f)
                print("✓ Loaded credentials from credentials.json")
        except Exception as e:
            print(f"✗ Error loading credentials: {e}")
            return None

    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def fetch_events_from_sheets():
    """Fetch all events from Google Sheets, excluding Leaves."""
    try:
        client = get_google_sheets_client()
        if not client:
            print("✗ Failed to initialize Google Sheets client")
            return []

        # Your Google Sheets ID from the app
        sheet_id = os.getenv('GOOGLE_SHEETS_ID', '1wpJSSYoHKKtzVN1e4X4b9pnrTNkVM0rMGBJubGh6xhk')
        print(f"Fetching events from sheet: {sheet_id}")
        spreadsheet = client.open_by_key(sheet_id)

        events = []
        event_id = 1

        # Get all worksheets except Leaves
        print(f"Reading worksheets...")
        for worksheet in spreadsheet.worksheets():
            if worksheet.title == "Leaves" or worksheet.title == "Useful Links":
                print(f"  Skipping {worksheet.title}")
                continue

            try:
                data = worksheet.get_all_records()
                print(f"  {worksheet.title}: {len(data)} records")
                for record in data:
                    # Get the date field - could be 'date', 'from_date', or 'to_date'
                    event_date = None
                    if 'date' in record and record['date']:
                        event_date = record['date']
                    elif 'from_date' in record and record['from_date']:
                        event_date = record['from_date']

                    if event_date:
                        event = {
                            'id': event_id,
                            'title': record.get('name', 'Unnamed Event'),
                            'type': worksheet.title,
                            'date': event_date,
                            'end_date': record.get('to_date', event_date),
                            'description': record.get('description', ''),
                            'engagement': record.get('engagement_app_entry', False),
                            'sa_id': record.get('sa_id', ''),
                            'assignees': record.get('assignees', '')
                        }
                        events.append(event)
                        event_id += 1
            except Exception as e:
                print(f"Error reading worksheet {worksheet.title}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"✓ Total events fetched: {len(events)}")
        return events
    except Exception as e:
        print(f"Error fetching from Google Sheets: {e}")
        return []

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APJ DemoX Events Calendar</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 30px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }

        .month-nav {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .month-nav button {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }

        .month-nav button:hover {
            background: #764ba2;
        }

        .month-year {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            min-width: 200px;
            text-align: center;
        }

        .legend {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }

        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }

        .calendar {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }

        .calendar thead {
            background: #f8f9fa;
        }

        .calendar th {
            padding: 15px;
            text-align: center;
            font-weight: 600;
            color: #333;
            border: 1px solid #e0e0e0;
        }

        .calendar td {
            padding: 0;
            border: 1px solid #e0e0e0;
            height: 120px;
            vertical-align: top;
            background: white;
            position: relative;
            cursor: pointer;
            transition: background 0.3s;
        }

        .calendar td:hover {
            background: #f8f9fa;
        }

        .calendar td.other-month {
            background: #f8f9fa;
            color: #ccc;
        }

        .date-number {
            padding: 8px;
            font-weight: 600;
            color: #333;
        }

        .date-number.other-month {
            color: #ccc;
        }

        .events-list {
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .event {
            font-size: 12px;
            padding: 4px 6px;
            border-radius: 3px;
            color: white;
            cursor: pointer;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            transition: transform 0.2s;
        }

        .event:hover {
            transform: scale(1.05);
        }

        .event-hands-on { background: #FFB6C1; color: #333; }
        .event-ai-agentic { background: #98FB98; color: #333; }
        .event-lunch-learn { background: #FFD700; color: #333; }
        .event-blueprint-workshop { background: #DDA0DD; color: #333; }
        .event-gtm-onboarding { background: #FFA500; color: #333; }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
        }

        .modal-title {
            font-size: 22px;
            font-weight: 600;
            color: #333;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 28px;
            cursor: pointer;
            color: #999;
            transition: color 0.3s;
        }

        .modal-close:hover {
            color: #333;
        }

        .modal-body {
            margin-bottom: 20px;
        }

        .event-detail {
            margin-bottom: 15px;
        }

        .event-detail-label {
            font-weight: 600;
            color: #667eea;
            font-size: 13px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .event-detail-value {
            color: #333;
            line-height: 1.6;
        }

        .event-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 5px;
        }

        .event-badge-yes {
            background: #E8F5E9;
            color: #2E7D32;
        }

        .event-badge-no {
            background: #FFEBEE;
            color: #C62828;
        }

        .modal-footer {
            text-align: right;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }

        .modal-footer button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }

        .modal-footer button:hover {
            background: #764ba2;
        }

        .emoji {
            margin-right: 8px;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .calendar td {
                height: 100px;
                font-size: 12px;
            }

            .date-number {
                padding: 5px;
            }

            .event {
                font-size: 11px;
            }

            .header h1 {
                font-size: 20px;
            }

            .controls {
                flex-direction: column;
            }

            .legend {
                gap: 10px;
            }

            .legend-item {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 APJ DemoX Events Calendar</h1>
            <p>View and manage all upcoming events</p>
        </div>

        <div class="controls">
            <div class="month-nav">
                <button onclick="previousMonth()">← Previous</button>
                <div class="month-year" id="monthYear"></div>
                <button onclick="nextMonth()">Next →</button>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #FFB6C1;"></div>
                <span>🎓 Hands on Experiences</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #98FB98;"></div>
                <span>🤖 AI Agentic Development</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFD700;"></div>
                <span>🥗 Lunch & Learn</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #DDA0DD;"></div>
                <span>🎪 Blueprint Workshops</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFA500;"></div>
                <span>🚀 GTM Onboarding</span>
            </div>
        </div>

        <div id="loadingMessage" class="loading">Loading events...</div>

        <table class="calendar" id="calendarTable" style="display: none;">
            <thead>
                <tr>
                    <th>Sun</th>
                    <th>Mon</th>
                    <th>Tue</th>
                    <th>Wed</th>
                    <th>Thu</th>
                    <th>Fri</th>
                    <th>Sat</th>
                </tr>
            </thead>
            <tbody id="calendarBody">
            </tbody>
        </table>
    </div>

    <!-- Event Details Modal -->
    <div class="modal" id="eventModal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <div class="modal-title" id="eventTitle"></div>
                </div>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="event-detail">
                    <div class="event-detail-label">Event Type</div>
                    <div class="event-detail-value" id="eventType"></div>
                </div>
                <div class="event-detail">
                    <div class="event-detail-label">Date</div>
                    <div class="event-detail-value" id="eventDate"></div>
                </div>
                <div class="event-detail">
                    <div class="event-detail-label">Description</div>
                    <div class="event-detail-value" id="eventDescription"></div>
                </div>
                <div class="event-detail">
                    <div class="event-detail-label">Engagement App Entry</div>
                    <div class="event-detail-value" id="eventEngagement"></div>
                </div>
                <div class="event-detail">
                    <div class="event-detail-label">SA ID</div>
                    <div class="event-detail-value" id="eventSAID"></div>
                </div>
                <div class="event-detail">
                    <div class="event-detail-label">Assignees</div>
                    <div class="event-detail-value" id="eventAssignees"></div>
                </div>
            </div>
            <div class="modal-footer">
                <button onclick="closeModal()">Close</button>
            </div>
        </div>
    </div>

    <script>
        let currentDate = new Date();
        let events = [];

        const eventTypeClasses = {
            "Hands on Experiences": "event-hands-on",
            "AI Assisted Agentic Development": "event-ai-agentic",
            "Lunch and Learns": "event-lunch-learn",
            "Blueprint Workshops": "event-blueprint-workshop",
            "GTM Onboarding": "event-gtm-onboarding"
        };

        // Fetch events from the server
        async function loadEvents() {
            try {
                const response = await fetch('/api/events');
                events = await response.json();
                document.getElementById('loadingMessage').style.display = 'none';
                document.getElementById('calendarTable').style.display = 'table';
                renderCalendar();
            } catch (error) {
                console.error('Error loading events:', error);
                document.getElementById('loadingMessage').innerHTML = '<span style="color: red;">Error loading events. Please make sure Google Sheets credentials are configured.</span>';
            }
        }

        function renderCalendar() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();

            // Update month/year display
            const monthNames = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"];
            document.getElementById("monthYear").textContent = `${monthNames[month]} ${year}`;

            // Get first day of month and number of days
            const firstDay = new Date(year, month, 1).getDay();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const daysInPrevMonth = new Date(year, month, 0).getDate();

            const calendarBody = document.getElementById("calendarBody");
            calendarBody.innerHTML = "";

            let dayCounter = 1;
            let nextMonthCounter = 1;

            for (let week = 0; week < 6; week++) {
                const row = document.createElement("tr");

                for (let day = 0; day < 7; day++) {
                    const cell = document.createElement("td");
                    const dateDiv = document.createElement("div");
                    dateDiv.className = "date-number";

                    if (week === 0 && day < firstDay) {
                        // Previous month days
                        dateDiv.className += " other-month";
                        dateDiv.textContent = daysInPrevMonth - firstDay + day + 1;
                        cell.className = "other-month";
                    } else if (dayCounter > daysInMonth) {
                        // Next month days
                        dateDiv.className += " other-month";
                        dateDiv.textContent = nextMonthCounter++;
                        cell.className = "other-month";
                    } else {
                        // Current month days
                        dateDiv.textContent = dayCounter;
                        const currentDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(dayCounter).padStart(2, "0")}`;
                        const dayEvents = events.filter(e => {
                            const eventStart = e.date;
                            const eventEnd = e.end_date || e.date;
                            return currentDateStr >= eventStart && currentDateStr <= eventEnd;
                        });

                        if (dayEvents.length > 0) {
                            const eventsList = document.createElement("div");
                            eventsList.className = "events-list";

                            dayEvents.forEach(event => {
                                const eventEl = document.createElement("div");
                                eventEl.className = `event ${eventTypeClasses[event.type] || ""}`;
                                eventEl.textContent = event.title;
                                eventEl.onclick = (e) => {
                                    e.stopPropagation();
                                    showEventDetails(event);
                                };
                                eventsList.appendChild(eventEl);
                            });

                            cell.appendChild(dateDiv);
                            cell.appendChild(eventsList);
                            dayCounter++;
                            row.appendChild(cell);
                            continue;
                        }

                        dayCounter++;
                    }

                    cell.appendChild(dateDiv);
                    row.appendChild(cell);
                }

                calendarBody.appendChild(row);
            }
        }

        function showEventDetails(event) {
            document.getElementById("eventTitle").textContent = event.title;
            document.getElementById("eventType").textContent = event.type;

            // Parse and format dates - handle date ranges
            const startDate = new Date(event.date + 'T00:00:00').toLocaleDateString("en-US", { weekday: "short", year: "numeric", month: "short", day: "numeric" });
            const endDate = event.end_date && event.end_date !== event.date
                ? new Date(event.end_date + 'T00:00:00').toLocaleDateString("en-US", { weekday: "short", year: "numeric", month: "short", day: "numeric" })
                : null;

            const dateText = endDate ? `${startDate} - ${endDate}` : startDate;
            document.getElementById("eventDate").textContent = dateText;

            document.getElementById("eventDescription").textContent = event.description || "No description provided";

            const engagementBadgeClass = event.engagement ? "event-badge-yes" : "event-badge-no";
            const engagementText = event.engagement ? "✓ Yes" : "✗ Not Created";
            document.getElementById("eventEngagement").innerHTML = `<span class="event-badge ${engagementBadgeClass}">${engagementText}</span>`;

            document.getElementById("eventSAID").textContent = event.sa_id || "N/A";
            document.getElementById("eventAssignees").textContent = event.assignees || "Not assigned";

            document.getElementById("eventModal").classList.add("active");
        }

        function closeModal() {
            document.getElementById("eventModal").classList.remove("active");
        }

        function previousMonth() {
            currentDate.setMonth(currentDate.getMonth() - 1);
            renderCalendar();
        }

        function nextMonth() {
            currentDate.setMonth(currentDate.getMonth() + 1);
            renderCalendar();
        }

        // Close modal when clicking outside
        document.getElementById("eventModal").addEventListener("click", function(e) {
            if (e.target === this) {
                closeModal();
            }
        });

        // Load events on page load
        loadEvents();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the calendar page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/events')
def get_events():
    """API endpoint to fetch events from Google Sheets."""
    events = fetch_events_from_sheets()
    return jsonify(events)

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check configuration."""
    return jsonify({
        'google_sheets_id_set': bool(os.getenv('GOOGLE_SHEETS_ID')),
        'google_creds_env_var_set': bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_STR')),
        'credentials_file_exists': os.path.exists('credentials.json'),
        'render_creds_file_exists': os.path.exists('/etc/render/credentials.json'),
        'sheet_id': os.getenv('GOOGLE_SHEETS_ID', '1wpJSSYoHKKtzVN1e4X4b9pnrTNkVM0rMGBJubGh6xhk')
    })

if __name__ == '__main__':
    print("Starting APJ DemoX Events Calendar Server...")
    port = int(os.getenv('PORT', 5000))
    print(f"Open http://0.0.0.0:{port} in your browser")
    app.run(host='0.0.0.0', port=port, debug=False)
