# utils/smartsheet_integration.py
import smartsheet
import streamlit as st
import pandas as pd

def update_smartsheet(dataframe: pd.DataFrame, sheet_id: str, demo_mode=True):
    """
    Upload the dataframe to a Smartsheet.
    In Demo Mode, simulate a successful upload.
    """
    if demo_mode:
        return True
    try:
        with open('credentials/smartsheet_token.txt', 'r') as f:
            access_token = f.read().strip()
        smart = smartsheet.Smartsheet(access_token)
        sheet = smart.Sheets.get_sheet(sheet_id).data
        column_map = {col.title: col.id for col in sheet.columns}
        
        new_rows = []
        for _, row in dataframe.iterrows():
            new_row = smartsheet.models.Row()
            new_row.to_top = True
            cells = []
            for col in dataframe.columns:
                if col in column_map:
                    cells.append({"column_id": column_map[col], "value": row[col]})
            new_row.cells = cells
            new_rows.append(new_row)
        
        smart.Sheets.add_rows(sheet_id, new_rows)
        return True
    except Exception as e:
        st.error(f"Error uploading to Smartsheet: {e}")
        return False
