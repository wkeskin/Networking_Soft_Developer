# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 15:07:15 2025

@author: ferre
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(user_input, threshold_low, threshold_high):
    """
    Sends an email notification when the user input is out of the specified range.
    """
    sender_email = "digitalmktgtrends@gmail.com"
    receiver_email = "comp216.grp2@gmail.com"
    password = "#########"  #API passsword will go here
    subject = "Alert: Input Out of Range"
    
    # Check if input is out of range
    if user_input < threshold_low:
        message_body = f"Warning: The entered value {user_input} is too low."
    elif user_input > threshold_high:
        message_body = f"Warning: The entered value {user_input} is too high."
    else:
        return
    
    # Email content setup
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_body, 'plain'))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP('smtp.sendgrid.net', 587)
        server.starttls()
        server.login('apikey', password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
