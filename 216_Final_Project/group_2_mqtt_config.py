# group_2_mqtt_config.py

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Topics
GROUP_ID = "group2"
BASE_TOPIC = f"iot/sensor/{GROUP_ID}"
STATUS_TOPIC = f"{BASE_TOPIC}/status/+"
CONTROL_TOPIC_BASE = f"iot/admin/{GROUP_ID}/control"
