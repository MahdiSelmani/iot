from config import *

def open_water_flow():
    global water_flow_active
    global fire_or_smoke_confirmed
    if fire_or_smoke_confirmed :
        water_flow_active = True
        print(f"\033[94m Water flow activated ... 💦💦💦 \033[0m")

def stop_water_flow():
    global water_flow_active
    if water_flow_active :
        print("\033[91m Water flow stopped ... ⛔⛔⛔ \033[0m")
        water_flow_active = False