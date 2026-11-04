# group_2_admin_app_fp.py
# Flask web application for administrator control (Bonus)

from flask import Flask, render_template, request, jsonify, Response
import csv
import threading
import time
import json
import paho.mqtt.client as mqtt
import random
from group_2_mqtt_config import MQTT_BROKER, MQTT_PORT, BASE_TOPIC, STATUS_TOPIC, CONTROL_TOPIC_BASE


# --- Configuration ---

MQTT_BROKER = "broker.hivemq.com"
#MQTT_BROKER = "localhost"
MQTT_PORT = 1883
CONTROL_TOPIC_BASE = "iot/admin/group2/control"
STATUS_TOPIC = "iot/sensor/group2/status/+"

# --- State Management ---
publisher_status = {}
subscriber_status = {}
status_lock = threading.Lock()
historical_data_log = []
MAX_LOG_SIZE = 1000
anomaly_log = []
MAX_ANOMALY_LOG = 200

app = Flask(__name__)

# --- MQTT Client Setup ---
admin_mqtt_client = None


def setup_admin_mqtt():
    global admin_mqtt_client
    try:
        client = mqtt.Client(
            client_id=f"admin_app_group2_{random.randint(1000,9999)}",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        connection_event = threading.Event()

        def on_connect(client, userdata, flags, rc, properties):
            if rc == 0:
                print("Admin MQTT connected successfully.")
                connection_event.set()
            else:
                print(f"Admin MQTT connection failed (Code: {rc})")

        client.on_connect = on_connect

        # Keep existing on_disconnect handler
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        # Wait up to 10 seconds for connection
        connection_event.wait(10)

        if connection_event.is_set():
            admin_mqtt_client = client
            print("Admin MQTT client ready.")
        else:
            print("Admin MQTT connection timeout (background reconnects will continue)")
            admin_mqtt_client = None  # Still allow background reconnects

    except Exception as e:
        print(f"Admin MQTT setup failed: {str(e)}")
        admin_mqtt_client = None

# --- MQTT Listener for Status Updates ---

def on_listener_connect(client, userdata, flags, rc, properties=None):
    """Callback when the status listener client connects."""
    if rc == 0:
        print("Status listener client connected successfully.")
        # Subscribe to the status topic
        client.subscribe(STATUS_TOPIC, qos=1)
        print(f"Subscribed to status topic: {STATUS_TOPIC}")
    else:
        print(f"Status listener failed to connect, return code {rc}\n")

def on_sensor_data(client, userdata, msg):
    print(f"✅ Sensor data received on {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        if all(k in data for k in ['sensor_id', 'value', 'timestamp']):
            log_data(data)
            print("📊 Logged historical data:", data)

            # Anomaly check
            if data['value'] < 19 or data['value'] > 29:
                log_anomaly("Out-of-Range", f"{data['sensor_id']} reported {data['value']}°C")
                print("🚨 Anomaly detected:", data)

        else:
            print("⚠️ Incomplete sensor data:", data)

    except Exception as e:
        print("❌ Error processing sensor data:", e)



def on_status_message(client, userdata, msg):
    """Callback when a status message is received."""
    print(f"Received status message on topic {msg.topic}")
    try:
        payload_str = msg.payload.decode('utf-8')
        status_data = json.loads(payload_str)

        # --- Basic Validation ---
        if not all(k in status_data for k in ['client_id', 'type', 'state', 'timestamp']):
            print(f"Received incomplete status message: {payload_str}")
            return

        client_id = status_data['client_id']
        client_type = status_data['type'].lower() # 'publisher' or 'subscriber'
        state = status_data['state']
        timestamp = status_data['timestamp']

        with status_lock: # Ensure thread-safe update of shared dictionaries
            if client_type == 'publisher':
                publisher_status[client_id] = {
                    'state': state,
                    'last_seen': timestamp
                }
                print(f"Updated publisher status for {client_id}: {publisher_status[client_id]}")
            elif client_type == 'subscriber':
                 subscriber_status[client_id] = {
                    'state': state,
                    'last_seen': timestamp,
                    'topic': status_data.get('topic', 'Unknown') # Capture topic
                }
                 print(f"Updated subscriber status for {client_id}: {subscriber_status[client_id]}")
            else:
                print(f"Received status from unknown client type '{client_type}' for ID {client_id}")

    except json.JSONDecodeError:
        print(f"Received non-JSON status message: {msg.payload.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Error processing status message: {e}")

def route_message(client, userdata, msg):
    if msg.topic.startswith("iot/sensor/group2/status/"):
        on_status_message(client, userdata, msg)
    else:
        on_sensor_data(client, userdata, msg)

def status_listener():
    try:
        listener = mqtt.Client(
            client_id=f"admin_listener_group2_{random.randint(1000,9999)}",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        # callbacks
        listener.on_message = route_message
        #listener.on_message = on_sensor_data
        #listener.on_message = on_status_message
        listener.on_connect = on_listener_connect

        # Add on_disconnect if needed

        listener.connect(MQTT_BROKER, MQTT_PORT, 60)
        listener.subscribe("iot/sensor/group2/status/+", qos=1)
        listener.subscribe("iot/sensor/group2/temprature", qos=1)  # Sensor data stream

        listener.loop_forever()  # Run in this thread
    except Exception as e:
        print(f"Status listener error: {e}")

# --- Data Logging
def log_data(data):
    historical_data_log.append(data)
    print("📊 log_data called:", data)
    print("📈 Historical log size:", len(historical_data_log))
    if len(historical_data_log) > MAX_LOG_SIZE:
        historical_data_log.pop(0)


def log_anomaly(anomaly_type, details):
    log_entry = {
        'timestamp': time.time(),
        'type': anomaly_type,
        'details': details
    }
    anomaly_log.append(log_entry)
    print("🚨 log_anomaly called:", log_entry)

    print("🚨 Anomaly log size:", len(anomaly_log))
    if len(anomaly_log) > MAX_ANOMALY_LOG:
        anomaly_log.pop(0)

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main admin dashboard page."""
    # Pass status information to the template
     # Create copies to avoid issues if dicts are updated while rendering
    current_publishers = publisher_status.copy()
    current_subscribers = subscriber_status.copy()
    return render_template('admin_dashboard.html',
                           publishers=publisher_status,
                           subscribers=subscriber_status)


@app.route('/api/config')
def get_config():
    return jsonify({
        'MQTT_BROKER': MQTT_BROKER,
        'MQTT_PORT': MQTT_PORT,
        'BASE_TOPIC': BASE_TOPIC,
        'STATUS_TOPIC': STATUS_TOPIC,
        'CONTROL_TOPIC_BASE': CONTROL_TOPIC_BASE
    })

@app.route('/api/status')
def get_status():
    """API endpoint to get current status."""
    now = time.time()
    with status_lock: # Read status safely
        # Tag clients as offline if they haven't sent status recently
        def enrich_status(data):
            enriched = {}
            for client_id, info in data.items():
                is_online = (now - info.get('last_seen', 0)) < 15  # 15 sec timeout
                enriched[client_id] = {
                    **info,
                    'is_online': is_online
                }
            return enriched

        return jsonify({
            'publishers': enrich_status(publisher_status),
            'subscribers': enrich_status(subscriber_status),
            'historical_data_count': len(historical_data_log),
            'anomaly_count': len(anomaly_log)
        })

@app.route('/api/historical')
def get_historical_data():
    """API endpoint for historical data (basic)."""
    # Add filtering by time range, sensor ID etc.
    start_time = request.args.get('start', type=float)
    end_time = request.args.get('end', type=float)

    temp_log = historical_data_log[:] # Create a copy for filtering

    filtered_data = temp_log # Replace with actual filtering logic
    if start_time:
         filtered_data = [d for d in filtered_data if d.get('timestamp', 0) >= start_time]
    if end_time:
         filtered_data = [d for d in filtered_data if d.get('timestamp', 0) <= end_time]

    # Return data for chart
    chart_data = [[d.get('timestamp') * 1000, d.get('value')] for d in filtered_data if 'timestamp' in d and 'value' in d]

    return jsonify(chart_data)

from datetime import datetime
@app.route('/api/anomalies')
def get_anomalies():
    """API endpoint for anomaly logs."""

    log_entry = {
    'timestamp': time.time(),
    'type': 'High Temperature',
    'details': 'Sensor group2_1 reported 32°C (Threshold: 30°C)',
    'severity': 'high'
}
    with status_lock:
        latest = anomaly_log[-10:]
        for entry in latest:
            entry['timestamp_str'] = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(latest)
    # anomaly_log.append(log_entry)
    # temp_anomalies = anomaly_log[:] # Create a copy
    # return jsonify(anomaly_log[-10:]) # Return last 10 anomalies

@app.route('/api/anomalies/clear', methods=['POST'])
def clear_anomalies():
    with status_lock:
        anomaly_log.clear()
    return jsonify({"status": "cleared"})

@app.route('/api/control/publisher/<publisher_id>', methods=['POST'])
def control_publisher(publisher_id):
    """API endpoint to send control commands to publishers."""
    command_data = request.get_json()
    if not command_data:
        return jsonify({'success': False, 'message': 'Invalid request body'}), 400

    command = request.json.get('command') # e.g., 'pause', 'resume', 'shutdown', 'set_interval'
    value = request.json.get('value') # Optional value for the command
    if not command:
         return jsonify({'success': False, 'message': 'Missing command in request'}), 400

    if not admin_mqtt_client or not admin_mqtt_client.is_connected():
        print("Admin command client not ready.")
        return jsonify({'success': False, 'message': 'Admin MQTT client not connected'}), 503

    control_message = json.dumps({'command': command, 'value': value})
    topic = f"{CONTROL_TOPIC_BASE}/publisher/{publisher_id}"
    print(f"Sending command to {topic}: {control_message}")

    try:
        msg_info = admin_mqtt_client.publish(topic, control_message, qos=1)
        msg_info.wait_for_publish(timeout=5.0) # Wait for PUBACK for QoS 1

        if msg_info.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Command '{command}' published successfully to {topic}")
            return jsonify({'success': True, 'message': f'Command {command} sent to {publisher_id}'})
        else:
             print(f"Failed to publish command to {topic}, rc={msg_info.rc}")
             return jsonify({'success': False, 'message': f'Failed to publish command (rc={msg_info.rc})'}), 500

    except ValueError as e: # Timeout error from wait_for_publish
        print(f"Timeout waiting for publish confirmation for command {command} to {topic}: {e}")
        return jsonify({'success': False, 'message': f'Timeout sending command: {e}'}), 504
    except Exception as e:
        print(f"Failed to send command to {topic}: {e}")
        return jsonify({'success': False, 'message': f'Failed to send command: {e}'}), 500


@app.route('/api/export', methods=['GET'])
def export_data():
    """Exports last 10 anomaly logs and summary statistics as CSV."""
    from collections import Counter

    # Get the last 10 anomalies
    recent_anomalies = anomaly_log[-10:]
    severity_counts = Counter([a.get("severity", "unknown") for a in recent_anomalies])

    def generate():
        yield "type,details,timestamp,severity\n"
        for anomaly in recent_anomalies:
            line = f"{anomaly.get('type')},{anomaly.get('details')},{anomaly.get('timestamp')},{anomaly.get('severity', 'unknown')}\n"
            yield line
        yield "\n"
        yield "Summary Statistics\n"
        yield f"Total anomalies: {len(recent_anomalies)}\n"
        for severity, count in severity_counts.items():
            yield f"{severity.capitalize()} anomalies: {count}\n"

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=data_export.csv"})

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Flask admin app...")
    # Start MQTT client for sending commands
    setup_admin_mqtt()

    # Start background thread for listening to status updates
    print("Starting status listener thread...")
    status_thread = threading.Thread(target=status_listener, daemon=True)
    status_thread.start()

    # Run Flask app
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    print("Flask admin app finished.")
