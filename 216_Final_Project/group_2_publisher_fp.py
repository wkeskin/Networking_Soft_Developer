# group_2_publisher_fp.py
# Implements the MQTT Publisher client with a GUI.

import paho.mqtt.client as mqtt
import paho.mqtt.properties as props
import paho.mqtt.packettypes as packettypes
import json
import time
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from group_2_data_generator_fp import SensorDataGenerator # Import group_2 data generator class
from group_2_mqtt_config import MQTT_BROKER, BASE_TOPIC

class PublisherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Publisher Control Panel")
        self.root.geometry("690x560")

        # --- MQTT Settings ---

        #self.broker_address = tk.StringVar(value=MQTT_BROKER)
        self.topic = tk.StringVar(value=f"{BASE_TOPIC}/temprature")  # or just BASE_TOPIC depending on usage
        self.broker_address = tk.StringVar(value="broker.hivemq.com")
        self.port = tk.IntVar(value=1883)
        #self.topic = tk.StringVar(value="iot/sensor/group2") # Use group_2 group's topic
        self.client_id = tk.StringVar(value=f"publisher_group2_{random.randint(100, 999)}")
        self.qos = tk.IntVar(value=1)
        self.mqtt_version = tk.StringVar(value="5") # Defaulting to MQTTv5

        # --- Data Generation Settings ---
        self.sensor_id = tk.StringVar(value="Sensor_group2_1")
        self.sensor_type = tk.StringVar(value="temperature")
        self.min_val = tk.DoubleVar(value=18.0)
        self.max_val = tk.DoubleVar(value=30.0)
        self.interval = tk.DoubleVar(value=2.0) # Publish interval in seconds
        self.miss_chance = tk.DoubleVar(value=0.01) # 1% chance to miss transmission [cite: 43]
        self.skip_block_chance = tk.DoubleVar(value=0.005) # 0.5% chance to skip a block [cite: 44]
        self.skip_block_duration = tk.IntVar(value=5) # Skip 5 transmissions if skipping block

        # --- State ---
        self.is_running = False
        self.is_skipping_block = False
        self.skip_block_counter = 0
        self.client = None
        self.thread = None
        self.generator = None

        # --- GUI ---
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- MQTT Config ---
        mqtt_frame = ttk.LabelFrame(main_frame, text="MQTT Configuration", padding="10")
        mqtt_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(mqtt_frame, text="Broker:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(mqtt_frame, textvariable=self.broker_address, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(mqtt_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(mqtt_frame, textvariable=self.port, width=7).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(mqtt_frame, text="Topic:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(mqtt_frame, textvariable=self.topic, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(mqtt_frame, text="Client ID:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(mqtt_frame, textvariable=self.client_id, width=20).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(mqtt_frame, text="QoS:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Combobox(mqtt_frame, textvariable=self.qos, values=[0, 1, 2], width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(mqtt_frame, text="MQTT Ver:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Combobox(mqtt_frame, textvariable=self.mqtt_version, values=["3.1.1", "5"], width=5).grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)


        # --- Sensor Config ---
        sensor_frame = ttk.LabelFrame(main_frame, text="Sensor Simulation", padding="10")
        sensor_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(sensor_frame, text="Sensor ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.sensor_id, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sensor_frame, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.sensor_type, width=15).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(sensor_frame, text="Min Value:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.min_val, width=7).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sensor_frame, text="Max Value:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.max_val, width=7).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(sensor_frame, text="Interval (s):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.interval, width=7).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sensor_frame, text="Miss Chance:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.miss_chance, width=7).grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(sensor_frame, text="Skip Block Chance:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.skip_block_chance, width=7).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sensor_frame, text="Skip Block Duration:").grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(sensor_frame, textvariable=self.skip_block_duration, width=7).grid(row=3, column=3, sticky=tk.W, padx=5, pady=2)


        # --- Controls ---
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(control_frame, text="Start Publishing", command=self.start_publishing)
        self.start_button.grid(row=0, column=0, padx=10)
        self.stop_button = ttk.Button(control_frame, text="Stop Publishing", command=self.stop_publishing, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10)

        # --- Status Log ---
        log_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(3, weight=1) # Allow log area to expand

        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = scrollbar.set

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END) # Scroll to the bottom
        self.log_text.config(state=tk.DISABLED)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        # Handle connection results for both v3.1.1 and v5
        if rc == 0:
            self.log_message(f"Connected to {self.broker_address.get()} (Code: {rc})")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.is_running = True
            # Start the publishing thread only after successful connection
            self.thread = threading.Thread(target=self.publish_loop, daemon=True)
            self.thread.start()
            #
            self.publish_status("running")
            # Subscribe to control topic
            control_topic = f"iot/admin/group2/control/publisher/{self.client_id.get()}"
            client.subscribe(control_topic, qos=1)
        else:
            self.log_message(f"Connection failed (Code: {rc})")
            messagebox.showerror("Connection Error", f"Failed to connect to MQTT Broker.\nResult Code: {rc}")
            self.stop_publishing() # Ensure state is reset

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            command = payload.get('command')
            
            if command == "pause":
                self.is_running = False
                self.publish_status("paused")
            elif command == "resume":
                self.is_running = True
                self.thread = threading.Thread(target=self.publish_loop)
                self.thread.start()
                self.publish_status("running")
            elif command == "shutdown":
                self.stop_publishing()
                
        except Exception as e:
            self.log_message(f"Error processing command: {e}")
    def on_disconnect(self, client, userdata, rc, properties=None):
         self.log_message(f"Disconnected (Code: {rc})")
         # Don't automatically stop publishing logic here if it might be a temporary drop
         # The publish loop will handle errors. We might want to implement auto-reconnect later.
         if self.is_running: # If we were intentionally running and got disconnected
             self.log_message("Connection lost. Attempting to reconnect...")
             # Implement reconnection logic if desired


    #def on_publish(self, client, userdata, mid, properties=None): # For v5
    def on_publish(self, client, userdata, mid, reason_code=0, properties=None):
    # def on_publish(self, client, userdata, mid): # Use this signature for v3.1.1
        # The correct signature depends on the protocol version used
        # For simplicity, just log the mid
        # print(f"Message {mid} published.") # Debug print
        pass # Keep GUI log cleaner
    
    def publish_status(self, state=None):
        if not self.client:
            self.log_message("MQTT client not connected. Skipping status publish.")
            return

        status_data = {
            "client_id": self.client_id.get(),
            "type": "publisher",
            "state": state if state else ("running" if self.is_running else "paused"),
            "timestamp": time.time(),
            "topic": self.topic.get()
        }
        status_topic = f"iot/sensor/group2/status/{self.client_id.get()}"

        try:
            self.client.publish(status_topic, json.dumps(status_data), qos=1)
            self.log_message(f"Status published to {status_topic}: {status_data}")
        except Exception as e:
            self.log_message(f"Failed to publish status: {e}")

    def start_publishing(self):
        self.log_message("Starting publisher...")

        # Initialize Data Generator
        try:
            self.generator = SensorDataGenerator(
                sensor_id=self.sensor_id.get(),
                sensor_type=self.sensor_type.get(),
                min_value=self.min_val.get(),
                max_value=self.max_val.get()
                # Add other generator params if needed
            )
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to create Data Generator: {e}")
            return

        # Configure MQTT Client based on selected version
        client_id = self.client_id.get()
        protocol_version = mqtt.MQTTv5 if self.mqtt_version.get() == "5" else mqtt.MQTTv311

        # Ensure unique client ID if running multiple instances
        if not client_id:
             client_id = f"publisher_{random.randint(1000, 9999)}"
             self.client_id.set(client_id)
             self.log_message(f"Generated Client ID: {client_id}")

        #self.client = mqtt.Client(client_id=client_id, protocol=protocol_version)
        self.client = mqtt.Client(
            client_id=client_id,
            protocol=protocol_version,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        # Assign callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        # Optional: Add TLS/SSL connection if needed
        # self.client.tls_set(ca_certs="ca.crt", certfile="client.crt", keyfile="client.key")

        try:
            broker = self.broker_address.get()
            port = self.port.get()
            self.log_message(f"Connecting to {broker}:{port}...")

            # Connect properties for v5
            connect_properties = None
            if protocol_version == mqtt.MQTTv5:
                connect_properties = props.Properties(packettypes.PacketTypes.CONNECT)
                connect_properties.SessionExpiryInterval = 30*60 # 30 minutes

            # Start connection attempt (non-blocking)
            self.client.connect_async(broker, port, 60, properties=connect_properties,clean_start=True)
            self.client.loop_start() # Start network loop in background thread

        except Exception as e:
            self.log_message(f"Error starting connection: {e}")
            messagebox.showerror("Connection Error", f"Error initiating connection: {e}")
            self.client = None


    def stop_publishing(self):
        self.log_message("Stopping publisher...")
        self.is_running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0) # Wait briefly for thread to exit

        if self.client:
            self.client.loop_stop() # Stop network loop
            try:
                self.client.disconnect()
            except Exception as e:
                self.log_message(f"Error during disconnect: {e}")
            self.client = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("Publisher stopped.")

        #send status
        self.publish_status("stopped")



    def publish_loop(self):
        while self.is_running:
            try:
                self.publish_status("running")  # Now matches method signature
                interval_sec = self.interval.get()
                time.sleep(interval_sec) # Wait for the specified interval

                if not self.client or not self.client.is_connected():
                    self.log_message("Waiting for connection...")
                    continue # Skip publish attempt if not connected

                # --- Simulate Skipping Blocks --- [cite: 44]
                if self.is_skipping_block:
                    self.skip_block_counter -= 1
                    if self.skip_block_counter <= 0:
                        self.is_skipping_block = False
                        self.log_message("Resuming normal transmission.")
                    else:
                        self.log_message(f"Skipping transmission (Block active: {self.skip_block_counter} left)")
                        continue # Skip this transmission

                if random.random() < self.skip_block_chance.get():
                    self.is_skipping_block = True
                    self.skip_block_counter = self.skip_block_duration.get()
                    self.log_message(f"--- Starting block skip ({self.skip_block_counter} transmissions) ---")
                    continue # Skip this transmission


                # --- Simulate Missing Individual Transmissions --- [cite: 43]
                if random.random() < self.miss_chance.get():
                    self.log_message("--- Simulating missed transmission ---")
                    # Need to get the next packet ID even if missed, so subscriber can detect gap
                    _ = self.generator.package_data() # Consume the packet ID increment
                    continue # Skip the actual publish


                # --- Generate and Publish Data ---
                data = self.generator.package_data()
                payload = json.dumps(data)
                current_qos = self.qos.get()
                current_topic = self.topic.get()

                # Publish properties (MQTTv5)
                publish_properties = None
                if self.client.protocol == mqtt.MQTTv5:
                     publish_properties = props.Properties(packettypes.PacketTypes.PUBLISH)
                     publish_properties.MessageExpiryInterval = 60 # Example: message expires in 60s
                     # Add other properties if needed

                # Publish the message
                msg_info = self.client.publish(current_topic, payload, qos=current_qos, properties=publish_properties)

                # Optional: Check if publish was queued successfully (for QoS 1 & 2)
                # if msg_info.rc == mqtt.MQTT_ERR_SUCCESS:
                #      self.log_message(f"Published PktID:{data['packet_id']} Val:{data['value']:.2f} (MID: {msg_info.mid})")
                # else:
                #      self.log_message(f"Failed to queue message PktID:{data['packet_id']} (Error: {msg_info.rc})")

                # Simple log without waiting for PUBACK/PUBCOMP
                self.log_message(f"Sent PktID:{data['packet_id']} Val:{data['value']:.2f}")


            except tk.TclError: # Handle errors if GUI is closed during sleep
                 self.log_message("GUI closed, stopping thread.")
                 self.is_running = False
                 break
            except AttributeError: # Handle case where client might become None unexpectedly
                 self.log_message("MQTT client is not available. Stopping.")
                 self.is_running = False
                 break
            except Exception as e:
                self.log_message(f"Error in publish loop: {e}")
                time.sleep(5) # Wait before retrying after an error

        self.log_message("Publish loop finished.")

    def on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("Quit", "Publisher is running. Stop and exit?"):
                self.stop_publishing()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PublisherApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # Handle window close button
    root.mainloop()