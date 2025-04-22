import requests
from bs4 import BeautifulSoup

# Function to scrape the Calendly booking confirmation (Simulated)
def scrape_appointment_status(email_body):
    """This function simulates scraping the Calendly booking confirmation link in the email body."""
    # You would typically extract the confirmation link from the email body. For now, we simulate the process.
    if "You have successfully scheduled" in email_body:  # Simulating the email content when an appointment is booked
        return True  # Appointment booked
    else:
        return False  # Appointment not booked
