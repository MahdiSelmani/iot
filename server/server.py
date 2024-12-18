import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

# MQTT Broker details
MQTT_BROKER = "0794f9505361427da75263ab96c4851d.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "rootroot"
MQTT_PASSWORD = "Rootroot+1"
MQTT_TOPIC = "firesmoke"  # Topic to subscribe to

# Flask app setup
app = Flask(__name__)
socketio = SocketIO(app)

# Global variables to hold the status of the fire/smoke detection
status = "OK"
last_alert_time = time.time()  # Start with the current time
status_reset_timer = None

# Callback when connected to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe to the topic
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code: {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    global status, last_alert_time
    try:
        # Decode the message payload
        message = msg.payload.decode("utf-8")
        
        if message == "Fire or smoke detected!":
            # Set status to ALERT and record the time of the alert
            status = "ALERT"
            socketio.emit('status_update', {'status': status})
            
            # Update last alert time
            last_alert_time = time.time()

    except Exception as e:
        print(f"Failed to process message: {e}")

# Function to monitor time and reset status if no message received in 5 seconds
def monitor_status():
    global last_alert_time, status
    while True:
        time.sleep(5)  # Check every second
        # If 5 seconds have passed since the last alert message, reset the status
        if time.time() - last_alert_time >= 5:
            if status != "OK":  # Only reset if status is not already "OK"
                status = "OK"
                socketio.emit('status_update', {'status': status})

# Function to handle water control
def control_water(action):    
    client.publish(MQTT_TOPIC, action)
    print(f"Water control command sent: {action}")

# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Function to start the MQTT client loop in a separate thread
def start_mqtt_loop():
    try:
        print("Connecting to MQTT Broker...")
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()  # Use loop_start to run it in the background
    except Exception as e:
        print(f"Failed to connect to MQTT Broker: {e}")

# Flask route to serve the HTML page
@app.route('/dashboard')
def index():
    return render_template('index.html')

# SocketIO event to toggle water control
@socketio.on('water_control')
def handle_water_control(action):
    # Extract the action sent from the frontend
    print(f"Received action: {action}")
    # Perform the corresponding action
    control_water(action)

if __name__ == "__main__":
    # Start MQTT client loop in a separate thread
    mqtt_thread = threading.Thread(target=start_mqtt_loop)
    mqtt_thread.daemon = True  # Allow thread to exit when the main program exits
    mqtt_thread.start()

    # Start the status monitoring thread
    status_monitoring_thread = threading.Thread(target=monitor_status)
    status_monitoring_thread.daemon = True  # Allow thread to exit when the main program exits
    status_monitoring_thread.start()

    # Start Flask web server on all network interfaces, port 5001
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
