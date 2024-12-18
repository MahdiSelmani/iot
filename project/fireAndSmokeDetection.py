import os
import signal
import cv2
from ultralytics import YOLO
import logging
from flask import Flask, Response
from threading import Thread
from water_flow import *
from config import *
from broker import *

# Disable ultralytics logs
logging.getLogger('ultralytics').setLevel(logging.ERROR)

fire_smoke_model = YOLO(custom_model_path)

# Ensure the directory exists for recording videos
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot access webcam.")
    exit()

# Flask app setup
app = Flask(__name__)

def generate_frames():
    global processed_frame
    while True:
        with frame_lock:
            if processed_frame is None:
                continue
            _, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def detection_loop():
    global recording, video_writer, fire_or_smoke_timer, fire_or_smoke_confirmed, processed_frame
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Cannot read frame from webcam.")
                break

            # Perform detection
            fire_smoke_results = fire_smoke_model(frame)[0]
            fire_or_smoke_detected = False

            # Draw bounding boxes and labels
            for result in fire_smoke_results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result
                if score > threshold:
                    label = fire_smoke_results.names[int(class_id)].upper()
                    color = (0, 0, 255) if label == "FIRE" else (255, 255, 0)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    text = f"{label}: {score:.2f}"
                    cv2.putText(frame, text, (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    fire_or_smoke_detected = True

            # Detection confirmation
            if fire_or_smoke_detected:
                if not fire_or_smoke_confirmed:
                    if fire_or_smoke_timer == 0:
                        fire_or_smoke_timer = time.time()
                    elif time.time() - fire_or_smoke_timer >= timeout_duration:
                        fire_or_smoke_confirmed = True
                        print("Detection confirmed: Fire or smoke detected.")
                        client.publish(MQTT_TOPIC, "Fire or smoke detected!")
                        print("Alert sent: Fire or smoke detected.")
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        video_filename = os.path.join(output_directory, f"alert_{timestamp}.avi")
                        video_writer = cv2.VideoWriter(
                            video_filename,
                            cv2.VideoWriter_fourcc(*'XVID'),
                            20.0,
                            (frame.shape[1], frame.shape[0])
                        )
                        recording = True
                        print(f"Recording started: {video_filename}")
                else:
                    if time.time() - fire_or_smoke_timer >= 3:
                        client.publish(MQTT_TOPIC, "Fire or smoke detected!")
                        fire_or_smoke_timer = time.time()

            else:
                fire_or_smoke_timer = 0
                fire_or_smoke_confirmed = False
                if recording:
                    video_writer.release()
                    print("Recording stopped.")
                    recording = False

            if recording and video_writer:
                video_writer.write(frame)

            with frame_lock:
                processed_frame = frame.copy()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        if recording and video_writer:
            video_writer.release()
        cap.release()
        cv2.destroyAllWindows()
        client.loop_stop()
        client.disconnect()
        print("Program terminated.")
        os.kill(os.getpid(), signal.SIGINT)

flask_thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False})
flask_thread.start()
detection_loop()
