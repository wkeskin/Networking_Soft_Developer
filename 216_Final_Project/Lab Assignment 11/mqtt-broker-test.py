import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print(f"Connection Result: {rc}")
    if rc == 0:
        print("Connected to HiveMQ broker successfully!")
        # Subscribe to a test topic
        client.subscribe("test/connection")
        
        # Publish a test message
        client.publish("test/connection", "Hello, HiveMQ!")

def on_message(client, userdata, message):
    print(f"Received message on topic {message.topic}")
    print(f"Message: {message.payload.decode()}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")

def main():
    # Create client
    client = mqtt.Client(client_id="test_connection_client")
    
    # Assign callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    # Connect to HiveMQ public broker
    broker = "broker.hivemq.com"
    port = 1883

    try:
        print(f"Attempting to connect to {broker}...")
        client.connect(broker, port, 60)

        # Start the loop
        client.loop_start()

        # Wait for a few seconds to see connection and messages
        time.sleep(10)

    except Exception as e:
        print(f"Connection error: {e}")
    
    finally:
        client.disconnect()
        print("Disconnected from broker")

if __name__ == "__main__":
    main()
