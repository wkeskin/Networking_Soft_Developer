# group_2_email_service_fp.py
# Based on Lab Assignment 8 group_2_email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os # Added for environment variables (recommended for credentials)

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email_alert(subject, message_body):
    """
    Sends an email notification using SMTP.
    It's recommended to use environment variables for credentials.
    """
    # --- Configuration ---
    smtp_server = 'smtp.sendgrid.net' 
    smtp_port = 587
    smtp_user = "apikey"
    # --- End Configuration ---

    if not all([smtp_server, smtp_port, smtp_user]):
        print("Email configuration is incomplete. Cannot send email.")
        return

    # Email content setup
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(message_body, 'plain'))

    try:
        # Connect to SMTP server
        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_user, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Email alert sent successfully!")
    except smtplib.SMTPAuthenticationError:
         print(f"Failed to send email: Authentication failed. Check username/password/API key.")
    except Exception as e:
        print(f"Failed to send email: {e}")



# Example usage (for testing this module)
if __name__ == "__main__":
     send_email_alert("Test Alert #2", "This is a test email for out-of-range data.")
     #send_email_alert("Test Missing Data", "This is a test email for missing data.")

