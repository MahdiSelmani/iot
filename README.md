# Fire and Smoke Detection Using Python

This project implements a fire and smoke detection system using Python and the Ultralytics library. It utilizes a dataset to train a model capable of detecting fire and smoke in images and video streams.

## Prerequisites

To run this project, you need the following:

- Python: Make sure you have Python installed on your system.
- Ultralytics YOLOv8: This project uses the Ultralytics YOLOv8 model for object detection. You can install it using pip:
- Paho-mqtt: Used to ensure connection to hivemq
  ```bash
  pip install ultralytics paho-mqtt flask

- CLone locally :
  ```bash
  git clone https://github.com/MahdiSelmani/iot.git

## Run
  Run detection program :
  ```bash
  cd project && python fireAndSmokeDetection.py
  ```

  Run web application and access on localhost:5001/dashboard :
  ```bash
  cd server && python server.py
  ```
