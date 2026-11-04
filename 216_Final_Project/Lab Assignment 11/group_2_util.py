import random
import time
import json

class Util:
    def __init__(self):
        self.start_id = 111  # Initial ID as specified
    
    def create_data(self, patient_name="P_FirstN P_LastN"):
        """
        Create a structured dictionary with patient monitoring data
        """
        data = {
            'id': self.start_id,  # Sequence number
            'patient': patient_name,  # Name of patient
            'time': time.asctime(),  # Time generated
            'heart_rate': int(random.gauss(80, 1)),  # Heart rate with slight variation
            'respiratory_rate': int(random.gauss(12, 2)),  # Respiratory rate
            'heart_rate_variability': 65,  # Fixed HRV for this example
            'body_temperature': round(random.gauss(99, 0.5), 1),  # Body temperature
            'blood_pressure': {
                'systolic': int(random.gauss(105, 2)),  # Systolic pressure
                'diastolic': int(random.gauss(70, 1))  # Diastolic pressure
            },
            'activity': random.choice(['Walking', 'Resting', 'Sleeping'])  # Random activity
        }
        
        # Increment start_id for next data generation
        self.start_id += 1
        
        return data
    
    def print_data(self, data):
        """
        Print the data in a human-readable format
        """
        print("Patient Monitoring Data:")
        print(f"ID: {data['id']}")
        print(f"Patient: {data['patient']}")
        print(f"Time: {data['time']}")
        print(f"Heart Rate: {data['heart_rate']} bpm")
        print(f"Respiratory Rate: {data['respiratory_rate']} breaths/min")
        print(f"Heart Rate Variability: {data['heart_rate_variability']}")
        print(f"Body Temperature: {data['body_temperature']}°F")
        print("Blood Pressure:")
        print(f"  Systolic: {data['blood_pressure']['systolic']} mmHg")
        print(f"  Diastolic: {data['blood_pressure']['diastolic']} mmHg")
        print(f"Activity: {data['activity']}")
        print("-" * 40)
