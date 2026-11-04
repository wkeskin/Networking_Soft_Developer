# group_2_subscriber_fp.py
# Implements the MQTT Subscriber client with a GUI for data display and alerting.

import paho.mqtt.client as mqtt
import paho.mqtt.properties as props
import paho.mqtt.packettypes as packettypes
import json
import time
import random
import collections
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from group_2_email_service_fp import send_email_alert # Import email function
from group_2_mqtt_config import MQTT_BROKER, BASE_TOPIC

class SubscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subscriber Dashboard")
        self.root.geometry("800x650")

        # --- MQTT Settings ---
        self.broker_address = tk.StringVar(value="broker.hivemq.com")
        #self.broker_address = tk.StringVar(value=MQTT_BROKER)
        self.topic = tk.StringVar(value=f"{BASE_TOPIC}/temprature")  # or just BASE_TOPIC depending on usage
   
        self.port = tk.IntVar(value=1883)
        #self.topic = tk.StringVar(value="iot/sensor/group2/temprature") # Subscribe to group topic hierarchy
        self.client_id = tk.StringVar(value=f"subscriber_group2_{random.randint(100, 999)}")
        self.qos = tk.IntVar(value=1)
        self.mqtt_version = tk.StringVar(value="5") # Defaulting to MQTTv5

        # --- Data Handling Settings ---
        self.buffer_size = tk.IntVar(value=50) # Number of data points for chart/analysis
        self.missing_data_timeout = tk.DoubleVar(value=10.0) # Seconds before flagging missing data
        self.out_range_low = tk.DoubleVar(value=19.0)
        self.out_range_high = tk.DoubleVar(value=29.0)
        self.alert_email_enabled = tk.BooleanVar(value=False) # Enable/disable email alerts

        # --- State ---
        self.is_connected = False
        self.client = None
        self.data_buffer = collections.deque(maxlen=self.buffer_size.get()) # Store {'ts': timestamp, 'value': value, 'id': pkt_id}
        self.last_packet_id = {} # Dictionary to track last ID per sensor: {sensor_id: last_id}
        self.last_message_time = {} # Dictionary to track last message time per sensor: {sensor_id: time}
        self.subscribed_topics = set() # Keep track of active subscriptions
        self.sensor_ids = set() # Track unique sensor IDs seen
        

        # --- GUI Elements ---
        self.figure = None
        self.ax = None
        self.canvas_widget = None
        self.create_widgets()
        self.log_message("Subscriber GUI loaded. Click 'Connect' to start.")
        # --- Missing Data Check ---
        self.missing_data_timer = None
        self.start_missing_data_check()


    def create_widgets(self):
        # Main layout frames
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        chart_frame = ttk.Frame(self.root, padding="5")
        chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        log_frame = ttk.Frame(self.root, padding="5")
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Connection Controls (Top Frame) ---
        conn_frame = ttk.LabelFrame(top_frame, text="Connection", padding="10")
        conn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(conn_frame, text="Broker:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(conn_frame, textvariable=self.broker_address, width=30).grid(row=0, column=1, padx=2)
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(conn_frame, textvariable=self.port, width=8).grid(row=0, column=3, padx=2)

        ttk.Label(conn_frame, text="Topic:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(conn_frame, textvariable=self.topic, width=30).grid(row=1, column=1, padx=2)
        ttk.Label(conn_frame, text="QoS:").grid(row=1, column=2, sticky=tk.W)
        ttk.Combobox(conn_frame, textvariable=self.qos, values=[0, 1, 2], width=4).grid(row=1, column=3, padx=2)

        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.connect_mqtt)
        self.connect_button.grid(row=0, column=4, rowspan=2, padx=10)
        self.disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_mqtt, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5, rowspan=2, padx=5)

        # --- Settings (Top Frame) ---
        settings_frame = ttk.LabelFrame(top_frame, text="Settings", padding="10")
        settings_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="Low (°C):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.out_range_low, width=5).grid(row=0, column=1)
        ttk.Label(settings_frame, text="High (°C):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.out_range_high, width=5).grid(row=1, column=1)
        ttk.Checkbutton(settings_frame, text="Email Alerts", variable=self.alert_email_enabled).grid(row=0, column=2, rowspan=2, padx=5)

        # --- Chart Area (Chart Frame) --- [Bonus: 55] (using Matplotlib)
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_title("Sensor Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.line, = self.ax.plot([], [], 'r-') # Initial empty line
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


        # --- Log Area (Log Frame) ---
        ttk.Label(log_frame, text="Log").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_area.pack(fill=tk.X, expand=True)

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    # --- MQTT Callbacks ---
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.publish_status("connected")  # Now matches method signature
            self.log_message(f"Connected to {self.broker_address.get()} (Code: {rc})")
            self.is_connected = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            # Subscribe after connection
            topic_to_sub = self.topic.get()
            qos_level = self.qos.get()
            self.log_message(f"Subscribing to '{topic_to_sub}' with QoS {qos_level}")
            self.client.subscribe(topic_to_sub, qos_level)
            self.subscribed_topics.add(topic_to_sub)

        else:
            self.log_message(f"Connection failed (Code: {rc})")
            messagebox.showerror("Connection Error", f"Failed to connect to MQTT Broker.\nResult Code: {rc}")
            self.disconnect_mqtt() # Reset state





    def on_disconnect(self, client, userdata, rc, properties=None, reason_code=None):
        self.log_message(f"Disconnected (Code: {rc})")
        self.is_connected = False
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.subscribed_topics.clear()
        # TODO: adding auto-reconnect logic here 
        self.publish_status("disconnected")


    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
         # properties is for v5, granted_qos is list for v5, int for v3
        self.log_message(f"Subscribed (MID: {mid}, Granted QoS: {granted_qos})")


    def on_unsubscribe(self, client, userdata, mid, properties=None, reason_codes=None):
        # reason_codes is for v5
        self.log_message(f"Unsubscribed (MID: {mid})")


    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode('utf-8')
            data = json.loads(payload_str) # Decode JSON [Bonus: 51]

            # --- Basic Validation ---
            if not all(k in data for k in ['packet_id', 'sensor_id', 'timestamp', 'value']):
                self.log_message(f"Received incomplete message on {msg.topic}: {payload_str}")
                return

            pkt_id = data['packet_id']
            sensor_id = data['sensor_id']
            ts = data['timestamp']
            value = data['value']

            self.log_message(f"RX ({msg.topic}): PktID:{pkt_id} Sensor:{sensor_id} Val:{value:.2f}")
            self.last_message_time[sensor_id] = time.time() # Update last seen time
            self.sensor_ids.add(sensor_id) # Track sensor

            # --- Store Data ---
            self.data_buffer.append({'ts': ts, 'value': value, 'id': pkt_id})
            # Ensure buffer size is updated if setting changes
            if len(self.data_buffer) > self.buffer_size.get():
                 self.data_buffer = collections.deque(list(self.data_buffer)[-self.buffer_size.get():], maxlen=self.buffer_size.get())
            

            # --- Check for Missing Packets --- 
            last_id = self.last_packet_id.get(sensor_id, None)
            if last_id is not None and pkt_id > last_id + 1:
                missing_count = pkt_id - (last_id + 1)
                log_msg = f"ALERT: Detected {missing_count} missing packet(s) from {sensor_id} (Last: {last_id}, Current: {pkt_id})"
                self.log_message(log_msg)
                if self.alert_email_enabled.get():
                    send_email_alert(f"Missing Data Alert ({sensor_id})", log_msg)
            self.last_packet_id[sensor_id] = pkt_id


            # --- Check for Out-of-Range Data --- 
            low_thresh = self.out_range_low.get()
            high_thresh = self.out_range_high.get()
            if value < low_thresh or value > high_thresh:
                log_msg = f"ALERT: Out-of-range value detected from {sensor_id}! Value: {value:.2f} (Range: {low_thresh}-{high_thresh})"
                self.log_message(log_msg)
                if self.alert_email_enabled.get():
                    send_email_alert(f"Out of Range Alert ({sensor_id})", log_msg)
            # --- Update Chart ---
            self.update_chart()

        except json.JSONDecodeError:
            self.log_message(f"Received non-JSON message on {msg.topic}: {msg.payload.decode('utf-8', errors='ignore')}")
        except Exception as e:
            self.log_message(f"Error processing message: {e}")
    
    
    def publish_status(self, state):
        status_data = {
            "client_id": self.client_id.get(),
            "type": "subscriber",
            "state": state,
            "timestamp": time.time(),
            "topic": self.topic.get()
        }
        status_topic = f"iot/sensor/group2/status/{self.client_id.get()}"
        try:
            self.client.publish(status_topic, json.dumps(status_data), qos=1)
            self.log_message(f"Status published to {status_topic}: {status_data}")

        except Exception as e:
            self.log_message(f"Failed to publish status: {e}")
    
    # --- MQTT Control ---
    def connect_mqtt(self):
        if self.is_connected:
            self.log_message("Already connected.")
            return

        self.log_message("Connecting to MQTT Broker...")

        client_id = self.client_id.get()
        protocol_version = mqtt.MQTTv5 if self.mqtt_version.get() == "5" else mqtt.MQTTv311

        if not client_id:
             client_id = f"subscriber_{random.randint(1000, 9999)}"
             self.client_id.set(client_id)
             self.log_message(f"Generated Client ID: {client_id}")

        #self.client = mqtt.Client(client_id=client_id, protocol=protocol_version)
        self.client = mqtt.Client(client_id=client_id, protocol=protocol_version, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe


        try:
            broker = self.broker_address.get()
            port = self.port.get()
            # Connect properties for v5 (e.g., clean start)
            connect_properties = None
            if protocol_version == mqtt.MQTTv5:
                connect_properties = props.Properties(packettypes.PacketTypes.CONNECT)
                connect_properties.SessionExpiryInterval = 0 # Non-persistent session

            self.client.connect_async(broker, port, 60, properties=connect_properties, clean_start=True) # Force clean start
            self.client.loop_start()

        except Exception as e:
            self.log_message(f"Error starting connection: {e}")
            messagebox.showerror("Connection Error", f"Error initiating connection: {e}")
            self.client = None


    def disconnect_mqtt(self):
        if not self.is_connected or not self.client:
            self.log_message("Not connected.")
            return

        self.log_message("Disconnecting...")
        if self.client:
            self.client.loop_stop()
            try:
                # Unsubscribe from all topics first (optional, good practice)
                for topic in list(self.subscribed_topics):
                     self.log_message(f"Unsubscribing from {topic}")
                     self.client.unsubscribe(topic)
                self.client.disconnect()
            except Exception as e:
                self.log_message(f"Error during disconnect/unsubscribe: {e}")
        # State updates happen in on_disconnect callback
        self.client = None # Clear client reference


    # --- Charting --- [Bonus: 55]
    def update_chart(self):
         if not self.data_buffer:
             return

         timestamps = [item['ts'] for item in self.data_buffer]
         values = [item['value'] for item in self.data_buffer]

         # Convert timestamps to relative time (seconds from start) or use datetime
         # For simplicity, using packet index for x-axis here
         # For real time axis, convert timestamps:
         # import datetime
         # times = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
         # self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))

         indices = range(len(values)) # Use simple index for x-axis

         self.line.set_data(indices, values)

         self.ax.relim() # Recalculate limits
         self.ax.autoscale_view(True, True, True) # Autoscale axes
         self.ax.set_xlabel(f"Last {len(values)} Readings") # Update x-label

         self.figure.canvas.draw_idle() # Schedule redraw efficiently


    # --- Missing Data Detection --- [Bonus: 57]
    def check_missing_data(self):
        self.publish_status("connected")  # Periodic heartbeat update
        now = time.time()
        timeout_sec = self.missing_data_timeout.get()

        if not self.is_connected: # Don't check if not connected
             self.schedule_next_check()
             return

        for sensor_id, last_time in list(self.last_message_time.items()):
            if now - last_time > timeout_sec:
                log_msg = f"ALERT: No data received from {sensor_id} for over {timeout_sec:.1f} seconds."
                self.log_message(log_msg)
                if self.alert_email_enabled.get():
                    send_email_alert(f"Missing Data Alert ({sensor_id})", log_msg)
                del self.last_message_time[sensor_id]

        self.schedule_next_check()

    def schedule_next_check(self):
         # Schedule the next check using root.after
         self.missing_data_timer = self.root.after(int(self.missing_data_timeout.get() * 1000 / 2), self.check_missing_data) # Check roughly twice per timeout period


    def start_missing_data_check(self):
        self.log_message("Starting missing data monitor.")
        self.schedule_next_check()

    def stop_missing_data_check(self):
        if self.missing_data_timer:
            self.root.after_cancel(self.missing_data_timer)
            self.missing_data_timer = None
            self.log_message("Stopped missing data monitor.")


    # --- Window Closing ---
    def on_closing(self):
        self.stop_missing_data_check() # Stop the check timer
        if self.is_connected:
            if messagebox.askokcancel("Quit", "Subscriber is connected. Disconnect and exit?"):
                self.disconnect_mqtt()
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriberApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()