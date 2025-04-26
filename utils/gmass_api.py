import requests

BASE_URL = "https://api.gmass.co/v1"

def send_email_gmass(api_key, subject, body, recipient):
    url = f"{BASE_URL}/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "subject": subject,
        "body": body,
        "recipients": [recipient],
        "isHtml": True
    }
    response = requests.post(url, headers=headers, json=payload)
    return (response.status_code == 200), response.json()

def get_quota(api_key):
    url = f"{BASE_URL}/quota"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    return response.json()

def get_campaign_status(api_key, campaign_id):
    url = f"{BASE_URL}/status/{campaign_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    return response.json()

def pause_campaign(api_key, campaign_id):
    url = f"{BASE_URL}/pause/{campaign_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, headers=headers)
    return response.json()

def resume_campaign(api_key, campaign_id):
    url = f"{BASE_URL}/resume/{campaign_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, headers=headers)
    return response.json()

def cancel_campaign(api_key, campaign_id):
    url = f"{BASE_URL}/cancel/{campaign_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, headers=headers)
    return response.json()
