import paho.mqtt.client as mqtt
import json
from group_2_util import Util  # Assuming the utility file is named group_2_util.py

# Create utility object for printing data
util = Util()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the topic
    client.subscribe("patient/monitoring")

def on_message(client, userdata, msg):
    try:
        # Decode the message
        payload = msg.payload.decode('utf-8')
        
        # Convert to dictionary
        data = json.loads(payload)
        
        # Print the data using utility function
        util.print_data(data)
    
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    # Create MQTT client
    client = mqtt.Client()
    
    # Assign callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker (test.mosquitto.org (port 1883), broker.hivemq.com (port 1883)), localhost,127..
    broker_address = "broker.hivemq.com"  # MQTT broker address
    broker_port = 1883  # Standard MQTT port

    client.connect(broker_address, broker_port)

    # Print startup message
    print("Waiting for messages. To exit, press CTRL+C")

    # Start the loop
    client.loop_forever()

if __name__ == "__main__":
    main()
