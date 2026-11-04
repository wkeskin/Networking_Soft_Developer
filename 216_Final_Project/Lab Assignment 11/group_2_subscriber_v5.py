import paho.mqtt.client as mqtt
import json
import signal
from group_2_util import Util

util = Util()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected (Code: {reason_code})")
    client.subscribe("patient/monitoring", qos=2)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        util.print_data(data)

        # Unsubscribe after 3 messages
        if data['id'] % 3 == 0:
            client.unsubscribe("patient/monitoring")
            print("Unsubscribed from topic")

    except Exception as e:
        print(f"Error: {e}")

def main():
    # Create MQTT v5 client with clean session
    client = mqtt.Client(
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    # Force clean session on every connection
    connect_properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
    connect_properties.SessionExpiryInterval = 0  # Immediate session cleanup

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.hivemq.com", 1883, clean_start=True, properties=connect_properties)
    client.loop_forever()

if __name__ == "__main__":
    main()