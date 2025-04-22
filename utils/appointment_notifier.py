import requests
import pandas as pd
import streamlit as st

def get_bookings():
    """
    Retrieve appointment bookings from Calendly's API.
    
    To use this integration:
    1. Generate a personal access token from Calendly and store it in st.secrets (e.g., CALENDLY_ACCESS_TOKEN).
    2. Ensure your Calendly account has scheduled events.
    
    Returns a DataFrame containing real-time booking data.
    """
    try:
        access_token = st.secrets["CALENDLY_ACCESS_TOKEN"]
    except Exception as e:
        return pd.DataFrame()
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = "https://api.calendly.com/scheduled_events"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame()
    
    data = response.json()
    events = []
    for item in data.get("collection", []):
        # Adjust these fields based on Calendly's API response.
        events.append({
            "Event Name": item.get("name", ""),
            "Start Time": item.get("start_time", ""),
            "Status": item.get("status", ""),
        })
    return pd.DataFrame(events)
