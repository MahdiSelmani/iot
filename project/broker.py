from config import *
import paho.mqtt.client as mqtt
from water_flow import *
import time

# MQTT Client setup
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set()
water_flow_active = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker.")
        client.subscribe(MQTT_TOPIC)  
    else:
        print(f"Failed to connect to MQTT Broker. Return code: {rc}")

def on_message(client, userdata, msg):
    global water_flow_active
    command = msg.payload.decode()
    if command == "OPEN":
        open_water_flow()
    elif command == "CLOSE":
        stop_water_flow()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker.")
        client.subscribe(MQTT_TOPIC)  
    else:
        print(f"Failed to connect to MQTT Broker. Return code: {rc}")

def on_message(client, userdata, msg):
    global water_flow_active
    command = msg.payload.decode()
    if command == "OPEN":
        open_water_flow()
    elif command == "CLOSE":
        stop_water_flow()

client.on_connect = on_connect
client.on_message = on_message


while not connected:
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        connected = True
    except Exception as e:
        print(f"Error connecting to MQTT Broker: {e}. Retrying in 5 seconds...")
        time.sleep(5)