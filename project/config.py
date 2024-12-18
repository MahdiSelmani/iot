from threading import Lock

threshold = 0.7
custom_model_path = './runs/detect/train/weights/best.pt'
MQTT_BROKER = "0794f9505361427da75263ab96c4851d.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "rootroot"
MQTT_PASSWORD = "Rootroot+1"
MQTT_TOPIC = "firesmoke" 
processed_frame = None
frame_lock = Lock()
output_directory = "./recordings"
# Recording and detection parameters
recording = False
video_writer = None
fire_or_smoke_timer = 0
timeout_duration = 3
fire_or_smoke_confirmed = True
water_flow_active = True
# Connect to the MQTT broker
connected = False