# utils/google_sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

def update_google_sheet(dataframe: pd.DataFrame, sheet_id: str, demo_mode=True):
    """
    Upload the dataframe to a Google Sheet.
    In Demo Mode, simulate a successful upload.
    """
    if demo_mode:
        return True
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/google_creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        sheet.clear()
        data = [dataframe.columns.values.tolist()] + dataframe.values.tolist()
        sheet.update(data)
        return True
    except Exception as e:
        st.error(f"Error uploading to Google Sheets: {e}")
        return False
