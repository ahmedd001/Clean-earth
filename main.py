import streamlit as st
import pandas as pd
import sqlite3
import time
import altair as alt
import plotly.express as px
import os
from io import BytesIO
from datetime import datetime
from jinja2 import Template
import asyncio
import warnings

import yagmail
from utils.seamless_ai import fetch_seamless_leads
from utils.email_sender import send_email_smtp
from utils.appointment_notifier import get_bookings

# Initialize an in-memory DataFrame to store email logs
email_logs_df = pd.DataFrame(columns=["recipient", "subject", "status", "error", "appointment_booked", "timestamp"])



# Suppress specific warnings (optional)
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure an event loop exists (for some environments)
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# For sentiment analysis
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
try:
    nltk.data.find("sentiment/vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")

# -------------------------
# Import functions from utils
# -------------------------
from utils.seamless_ai import fetch_seamless_leads
from utils.email_sender import send_email_smtp
from utils.appointment_notifier import get_bookings

# -------------------------
# Database Functions (SQLite)
# -------------------------
DB_FILE = "clean_earth_leads.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            subject TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            error TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def log_email(recipient, subject, status, error=""):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO email_logs (recipient, subject, status, error) VALUES (?, ?, ?, ?)",
        (recipient, subject, status, error),
    )
    conn.commit()
    conn.close()

def fetch_email_logs():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM email_logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

init_db()

# -------------------------
# Utility: Sentiment Analysis
# -------------------------
def analyze_sentiment(text):
    """Perform sentiment analysis using VADER."""
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

# -------------------------
# STREAMLIT CONFIG & DARK THEME
# -------------------------
st.set_page_config(
    page_title="Clean Earth - Lead Automation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* Global Dark Background */
body, .reportview-container, .main, .block-container {
    background-color: #1E1E1E !important;
    color: #ECECEC !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
/* Sidebar */
.sidebar .sidebar-content {
    background-color: #2A2A2A !important;
    color: #FFFFFF !important;
}
/* Container Padding */
.block-container {
    padding: 1.5rem 2rem;
}
/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 700;
}
/* Hero Section */
.hero-container {
    background: linear-gradient(135deg, #222 0%, #333 100%);
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 1rem;
    position: relative;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    color: #ffffff;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #cccccc;
    margin-bottom: 1rem;
    line-height: 1.4em;
}
.hero-icons {
    display: flex;
    gap: 2rem;
    justify-content: center;
    margin-top: 1rem;
}
/* Feature Cards */
.feature-card {
    background-color: #2A2A2A;
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
    color: #FFFFFF;
}
.feature-card h4 {
    margin-top: 1rem;
    font-size: 1.2rem;
}
.feature-card p {
    font-size: 0.95rem;
    color: #CCCCCC;
}
.icon-container {
    width: 60px;
    margin: 0 auto;
}
/* Buttons */
.stButton>button, .stDownloadButton>button {
    background-color: #3C3C3C !important;
    color: #FFFFFF !important;
    border-radius: 5px !important;
    border: none !important;
    padding: 0.6rem 1rem !important;
    font-size: 1rem !important;
    cursor: pointer !important;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    background-color: #505050 !important;
}
/* DataFrame Tables */
[data-testid="stDataFrame"] {
    border: 1px solid #444444 !important;
    border-radius: 5px !important;
    color: #ECECEC !important;
}
/* Footer */
.footer {
    text-align: center;
    color: #888888;
    margin-top: 20px;
    font-size: 0.9rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------
# SIDEBAR WIDGETS (Production Mode Only)
# -------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8243/8243863.png", width=60)
st.sidebar.title("Clean Earth Dashboard")
st.sidebar.info("This app uses Gmail SMTP, VADER, and Plotly.")

# -------------------------
# NAVIGATION TABS
# -------------------------
TABS = [
    "Home", "Upload & Segment", "Email Campaign",
    "Analytics", "Calendly / Appointments", "Sentiment Analysis"
]
page = st.selectbox("Navigate", TABS)

# -------------------------
# HOME PAGE
# -------------------------
if page == "Home":
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Clean Earth - Lead Automation Dashboard</div>
            <div class="hero-subtitle">
                The all-in-one platform for eco-friendly outreach.
            </div>
            <div class="hero-icons">
                <img src="https://cdn-icons-png.flaticon.com/512/2370/2370376.png" width="50" height="50"/>
                <img src="https://cdn-icons-png.flaticon.com/512/5948/5948511.png" width="50" height="50"/>
                <img src="https://cdn-icons-png.flaticon.com/512/3649/3649057.png" width="50" height="50"/>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-container">
                    <img src="https://cdn-icons-png.flaticon.com/512/2370/2370376.png" width="40" height="40"/>
                </div>
                <h4>Bulk Upload</h4>
                <p>Ingest and segment your leads.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-container">
                    <img src="https://cdn-icons-png.flaticon.com/512/5948/5948511.png" width="40" height="40"/>
                </div>
                <h4>Automated Emails</h4>
                <p>Send personalized campaigns via Gmail SMTP.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-container">
                    <img src="https://cdn-icons-png.flaticon.com/512/3649/3649057.png" width="40" height="40"/>
                </div>
                <h4>Interactive Analytics</h4>
                <p>Visualize performance with dynamic charts.</p>
            </div>
            """, unsafe_allow_html=True
        )
    st.markdown("---")
    st.subheader("Fetch Leads from Seamless AI")
    if "SeamlessData" not in st.session_state:
        st.session_state["SeamlessData"] = pd.DataFrame()
    api_key = st.text_input("Enter your Seamless.AI API Key", type="password")
    if st.button("Fetch Leads from Seamless.AI"):
        df_seamless = fetch_seamless_leads(api_key)
        if not df_seamless.empty:
            st.success("Fetched leads successfully!")
            st.dataframe(df_seamless)
            st.session_state["SeamlessData"] = df_seamless.copy()
        else:
            st.error("No leads found or API call failed.")
    st.markdown(f"<div class='footer'>© {datetime.now().year} Clean Earth. All rights reserved.</div>", unsafe_allow_html=True)

# -------------------------
# UPLOAD & SEGMENT PAGE
# -------------------------
elif page == "Upload & Segment":
    st.header("Upload & Segment Leads")
    st.write("Upload your CSV/Excel file to clean and segment your data.")
    uploaded_file = st.file_uploader("Upload (CSV/Excel)", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.write("**Data Preview**")
            st.dataframe(df.head())
            if st.button("Clean & Segment"):
                df.dropna(subset=["Email"], inplace=True)
                for col in df.select_dtypes(include='object').columns:
                    df[col] = df[col].str.strip()
                st.success("Data cleaned successfully!")
                if "Company" in df.columns:
                    company_counts = df["Company"].value_counts()
                    chart_data = pd.DataFrame({"Company": company_counts.index, "Count": company_counts.values})
                    chart = px.bar(chart_data, x="Company", y="Count", title="Leads per Company", template="plotly_dark")
                    st.plotly_chart(chart, use_container_width=True)
                st.session_state["CleanedData"] = df.copy()
                st.write("**Cleaned Data**")
                st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.info("Please upload a leads file.")

#email page


# … inside your EMAIL CAMPAIGN tab …
elif page == "Email Campaign":
    st.header("Bulk Email Campaign")
    if "CleanedData" not in st.session_state or st.session_state["CleanedData"].empty:
        st.warning("Please upload & clean leads first.")
        st.stop()

    df = st.session_state["CleanedData"]
    st.dataframe(df.head())

    # SMTP credentials & subject
    col1, col2 = st.columns(2)
    with col1:
        sender_email = st.text_input("Your Gmail Address")
    with col2:
        sender_password = st.text_input("Gmail App Password", type="password")
    subject = st.text_input("Email Subject", "Greetings from Clean Earth")

    # Load HTML template
    tpl_path = os.path.join("Template", "email.html")
    tpl_str = open(tpl_path, "r", encoding="utf-8").read()

    if st.checkbox("Use custom HTML template?"):
        uploaded = st.file_uploader("Upload HTML", type="html")
        if uploaded:
            tpl_str = uploaded.read().decode("utf-8")

    # Optional attachment
    file_attach = st.file_uploader(
        "Attachment (PDF/DOCX/PNG/JPG)", ["pdf","docx","png","jpg"], key="attachment"
    )

    if st.button("Send Emails"):
        total = len(df)
        sent = 0
        progress = st.progress(0)

        # initialize SMTP
        yag = yagmail.SMTP(user=sender_email, password=sender_password)

        for i, row in df.iterrows():
            progress.progress((i + 1) / total)
            to = row.get("Email")
            if not to or pd.isna(to):
                continue

            # Render with Jinja (passes CalendlyLink into your <a href="{{ CalendlyLink }}">
            html_body = Template(tpl_str).render(
                FirstName    = row.get("First Name", "Friend"),
                LastName     = row.get("Last Name", ""),
                Company      = row.get("Company", "your company"),
                CalendlyLink = "https://calendly.com/clean-earth"
            )

            # Build contents: HTML + any attachment
            contents = [html_body]
            if file_attach:
                bio = BytesIO(file_attach.read())
                bio.name = file_attach.name
                contents.append(bio)

            try:
                yag.send(to=to, subject=subject, contents=contents)
                sent += 1
            except Exception as e:
                st.error(f"❌ Failed to send to {to}: {e}")

        st.success(f"✅ Emails sent to {sent} out of {total} contacts!")




# -------------------------
# LOGS PAGE
# -------------------------
elif page == "Logs":
    st.header("Email Logs")
    
    if email_logs_df.empty:
        st.info("No logs available. Send some emails first!")
    else:
        st.write("**Email Logs**")
        st.dataframe(email_logs_df)




# -------------------------
# ANALYTICS PAGE
# -------------------------
elif page == "Analytics":
    st.header("Campaign Analytics & Follow-Up")
    logs = fetch_email_logs()
    
    if logs.empty:
        st.info("No email logs yet. Send some emails first!")
    else:
        # Display Email Logs
        st.write("**Email Logs**")
        st.dataframe(logs)
        
        # Show the send status chart
        status_counts = logs['status'].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        bar_chart = px.bar(status_counts, x="Status", y="Count", title="Email Send Status", template="plotly_dark")
        st.plotly_chart(bar_chart, use_container_width=True)

        # Show the timeline of emails sent
        logs['timestamp'] = pd.to_datetime(logs['timestamp'])
        timeline_data = logs.groupby(logs['timestamp'].dt.date).size().reset_index(name='Count')
        line_chart = px.line(timeline_data, x="timestamp", y="Count", title="Email Sends Timeline", markers=True, template="plotly_dark")
        st.plotly_chart(line_chart, use_container_width=True)

        st.subheader("Follow-Up Emails")

        # Filter emails that are sent but appointment was not booked
        no_appointment = logs[logs['appointment_booked'] == False]

 


# -------------------------
# CALENDLY / APPOINTMENTS PAGE
# -------------------------
elif page == "Calendly / Appointments":
    st.header("Schedule Meetings via Calendly")
    calendly_link = st.text_input("Your Calendly Link", "https://calendly.com/clean-earth")
    if st.button("Embed Calendly"):
        if "calendly.com" in calendly_link:
            st.components.v1.iframe(src=calendly_link, width="100%", height=800, scrolling=True)
        else:
            st.error("Please enter a valid Calendly link.")
    st.info("Contacts can book a meeting directly via the embedded Calendly page.")
    from utils.appointment_notifier import get_bookings
    st.markdown("---")
    st.subheader("Appointment Bookings")
    bookings = get_bookings()
    if not bookings.empty:
        st.dataframe(bookings)
    else:
        st.info("No appointment data available. Integrate your booking system for real data.")

# -------------------------
# SENTIMENT ANALYSIS PAGE
# -------------------------
elif page == "Sentiment Analysis":
    st.header("Sentiment Analysis")
    st.write("Paste a lead response or email content to evaluate its sentiment using VADER.")
    sample_response = st.text_area("Enter text for sentiment analysis", "")
    if st.button("Analyze Sentiment"):
        if sample_response.strip():
            sentiment = analyze_sentiment(sample_response)
            st.write("Sentiment Scores:", sentiment)
            compound = sentiment.get("compound", 0)
            if compound >= 0.05:
                score = "Positive"
            elif compound <= -0.05:
                score = "Negative"
            else:
                score = "Neutral"
            st.success(f"Final Sentiment: {score} (Compound Score: {compound})")
        else:
            st.error("Please enter some text to analyze.")

# -------------------------
# FOOTER
# -------------------------
st.markdown(f"<div class='footer'>© {datetime.now().year} Clean Earth. All rights reserved.</div>", unsafe_allow_html=True)
