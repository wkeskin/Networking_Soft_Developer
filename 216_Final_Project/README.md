# COMP216 Final Project – Group 2
- Aiko Bislig  
- Jacob Ferreira  
- Lissette Gorrin Rodriguez  
- Samer Aljundi Al Fattouhi Aljundi  
- Wardatul Keskin


## 🔍 Project Overview
This project demonstrates an end-to-end IoT system using MQTT for real-time sensor simulation and monitoring.

### Project Structure:

| Component          | Description                                            |
|--------------------|--------------------------------------------------------|
| **Publisher**      | GUI to simulate patterned temperature data             |
| **Subscriber**     | GUI to visualize, detect anomalies, and send alerts    |
| **Admin App**      | Flask web dashboard to control and monitor clients     |
| **Data Generator** | Class for creating sensor data with trends and noise   |
| **Email Alerts**   | Sends email alerts for wild values or missing data     |
| **MQTT Config**    | Central MQTT constants used across modules             |

### System Architecture

[PUBLISHER] ---> MQTT Broker ---> [SUBSCRIBER]
                                ↘
                          [ADMIN DASHBOARD]


---
## 🛠 Requirements

- Python 3.9 or later
- Required libraries:
  ```bash
  pip install paho-mqtt flask matplotlib

---

## SMTP Email Setup
1. Copy the template file: cp .env_template .env
2. Edit .env with your credentials:
   SENDER_EMAIL=your_sender@example.com
   RECEIVER_EMAIL=your_receiver@example.com
   SMTP_PASSWORD=your_smtp_api_key_or_app_password

---

## How to Run the Project
1. Start Admin Dashboard
   python group_2_admin_app_fp.py
2. Opens a Flask server at http://localhost:5001
3. Start Publisher GUI
   python group_2_publisher_fp.py

4. Start Subscriber GUI
   python group_2_subscriber_fp.py


