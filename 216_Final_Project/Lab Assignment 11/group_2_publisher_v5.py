import paho.mqtt.client as mqtt
import json
import time
from group_2_util import Util

def on_publish(client, userdata, mid, properties=None):  # Update the callback function signature
    print(f"Message {mid} published")
    if properties:
        print(f"  Properties: {properties}")

def main():
    client = mqtt.Client(protocol=mqtt.MQTTv5)

    # Set the new on_publish callback
    client.on_publish = on_publish

    client.max_inflight_messages_set(5)

    connect_properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
    connect_properties.SessionExpiryInterval = 300

    client.connect("broker.hivemq.com", 1883, clean_start=True, properties=connect_properties)

    util = Util()
    try:
        for i in range(5):
            data = util.create_data()
            payload = json.dumps(data)

            # Set publishing properties
            publish_properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
            publish_properties.MessageExpiryInterval = 60  # Message expires in 60s

            # Alternate between QoS 1 and 2
            qos = 2 if i % 2 == 0 else 1
            retain = True if i == 4 else False  # Retain last message

            # Publish with QoS and properties
            client.publish(
                "patient/monitoring",
                payload,
                qos=qos,
                retain=retain,
                properties=publish_properties
            )

            util.print_data(data)
            time.sleep(2)

    finally:
        client.disconnect()

if __name__ == "__main__":
    main()