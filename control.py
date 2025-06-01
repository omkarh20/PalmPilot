import serial
import time
import pyautogui
import json

with open("gesture_mappings.json", "r") as f:
    gesture_map = json.load(f)
    
ArduinoSerial = serial.Serial('com4', 9600)
time.sleep(2)

while True:
    incoming = str(ArduinoSerial.readline().decode('utf-8')).strip()
    print(incoming)

    for gesture, action in gesture_map.items():
        if gesture in incoming:
            action_type = action.get("type")

            if action_type == "key_press":
                pyautogui.press(action["key"])

            elif action_type == "key_sequence":
                pyautogui.typewrite(action["keys"], interval=0.2)

            elif action_type == "hotkey":
                pyautogui.hotkey(*action["keys"])

            elif action_type == "hotkey_repeat":
                for _ in range(action.get("repeat", 1)):
                    pyautogui.hotkey(*action["keys"])
                    time.sleep(0.1)
            break
