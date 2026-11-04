import paho.mqtt.client as mqtt
import json
import time
from group_2_util import Util  # Assuming the utility file is named group_2_util.py

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")

def main():
    # Create MQTT client
    client = mqtt.Client()
    client.on_publish = on_publish

    # Connect to broker (test.mosquitto.org (port 1883), broker.hivemq.com (port 1883)), localhost,127..
    broker_address = "broker.hivemq.com"  # MQTT broker address
    broker_port = 1883  # Standard MQTT port

    client.connect(broker_address, broker_port)

    # Create utility object
    util = Util()

    # Publish messages in a loop
    try:
        for _ in range(5):  # Publish 5 messages
            # Create data
            data = util.create_data()
            
            # Convert to JSON string
            payload = json.dumps(data)
            
            # Publish to a topic
            topic = "patient/monitoring"
            client.publish(topic, payload)
            
            # Print the data
            util.print_data(data)
            
            # Wait between publishes
            time.sleep(2)
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Disconnect
        client.disconnect()

if __name__ == "__main__":
    main()
