import cv2
import time
import math as m
import mediapipe as mp
import os

import requests
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
from typing import Dict, NoReturn
import json
import datetime


# Calculate distance
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


# Calculate angle.
def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = 180 / m.pi * theta
    return degree


"""
Function to send alert. Use this function to send alert when bad posture detected.
Feel free to get creative and customize as per your convenience.
"""


def sendWarning(x):
    pass

def login(trial: int = 0) -> Dict:
    if trial >= 5:
        return {}
    user_name: str = input()
    password: str = input()
    auth = HTTPBasicAuth(user_name, password)
    try:
        res = requests.get(f"{API_URL}/user/auth/", auth=auth)
        res.raise_for_status()
        user = res.json()
        return user
    except HTTPError as e:
        print(e)
        return login(trial + 1)
    
def calibrate(offset) -> NoReturn:
    data = json.dumps({"neck_angle_offset": offset})
    user_id: int = user["id"]
    try:
        res = requests.put(f"{API_URL}/user/calibration/external-posture/{user_id}", data)
        res.raise_for_status()
        return
    except HTTPError as e:
        print(e)
        return
    finally:
        return

def post(neck_angle: float, torso_angle, now: datetime) -> NoReturn:
    if len(user) <= 0:
        return
    data = json.dumps({
        "user_id": user["id"],
        "neck_angle": neck_angle,
        "torso_angle": torso_angle,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S.%f")
    })
    try:
        res = requests.post(f"{API_URL}/external-posture/", data)
        res.raise_for_status()
        return
    except HTTPError as e:
        print(e)
        return
    finally:
        return

# =============================CONSTANTS and INITIALIZATIONS=====================================#
# Initilize frame counters.
good_frames = 0
bad_frames = 0

# Font type.
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 3
font_thickness = 10

# Colors.
blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
black = (0, 0, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

expand_offset = 400

# Initialize mediapipe pose class.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

API_URL: str = "http://localhost:4201"
NECK_ANGLE_OFFSET: float = 0
user = {}
is_sending: bool = False
# ===============================================================================================#


if __name__ == "__main__":
    user = login()
    os.makedirs(f"images/{user['id']}", exist_ok=True)
    cap = cv2.VideoCapture(0)
    cap.set(3, 2000)
    cap.set(4, 2000)

    while True:
        # Capture frames.
        ret, image = cap.read()
        if not ret:
            continue
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        h, w = image.shape[:2]
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image.
        keypoints = pose.process(image)

        # Convert the image back to BGR.
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Use lm and lmPose as representative of the following methods.
        lm = keypoints.pose_landmarks
        lmPose = mp_pose.PoseLandmark
        if lm is None or lmPose is None:
            continue

        # Acquire the landmark coordinates.
        # Once aligned properly, left or right should not be a concern.      
        # Left shoulder.
        l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
        l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
        # Right shoulder
        r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
        r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
        # Left ear.
        l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
        l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
        # Left hip.
        l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
        l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

        # Calculate distance between left shoulder and right shoulder points.
        offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

        # Assist to align the camera to point at the side view of the person.
        # Offset threshold 30 is based on results obtained from analysis over 100 samples.
        if offset < 100:
            cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), font, font_scale, black, font_thickness)
        else:
            cv2.putText(image, str(int(offset)) + ' Not Aligned', (w - 150, 30), font, font_scale, red, font_thickness)

        # get input key
        key = cv2.waitKey(1)
        # presse enter key
        if key == 13:
            NECK_ANGLE_OFFSET = neck_inclination
            calibrate(neck_inclination)
        
        # Calculate angles.
        neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
        torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)
        neck_angle: float = neck_inclination - NECK_ANGLE_OFFSET

        # Draw landmarks.
        cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
        cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)

        # Let's take y - coordinate of P3 100px above x1,  for display elegance.
        # Although we are taking y = 0 while calculating angle between P1,P2,P3.
        cv2.circle(image, (l_shldr_x, l_shldr_y - expand_offset), 7, yellow, -1)
        cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
        cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)

        # Similarly, here we are taking y - coordinate 100px above x1. Note that
        # you can take any value for y, not necessarily 100 or 200 pixels.
        cv2.circle(image, (l_hip_x, l_hip_y - expand_offset), 7, yellow, -1)

        # Put text, Posture and angle inclination.
        # Text string for display.
        angle_text_string = 'Neck : ' + str(int(neck_angle)) + '  Torso : ' + str(int(torso_inclination))

        # Determine whether good posture or bad posture.
        # The threshold angles have been set based on intuition.
        if neck_angle < 40 and torso_inclination < 10:
            bad_frames = 0
            good_frames += 1
            
            cv2.putText(image, angle_text_string, (10, 100), font, font_scale, black, font_thickness)
            cv2.putText(image, str(int(neck_angle)), (l_shldr_x + 10, l_shldr_y), font, font_scale, black, font_thickness)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, font_scale, black, font_thickness)

            # Join landmarks.
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), black, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - expand_offset), black, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), black, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - expand_offset), black, 4)

        else:
            good_frames = 0
            bad_frames += 1

            cv2.putText(image, angle_text_string, (10, 100), font, font_scale, red, font_thickness)
            cv2.putText(image, str(int(neck_angle)), (l_shldr_x + 10, l_shldr_y), font, font_scale, red, font_thickness)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, font_scale, red, font_thickness)

            # Join landmarks.
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - expand_offset), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - expand_offset), red, 4)

        # Calculate the time of remaining in a particular posture.
        good_time = (1 / fps) * good_frames
        bad_time =  (1 / fps) * bad_frames

        # # Pose time.
        # if good_time > 0:
        #     time_string_good = 'Good Posture Time : ' + str(round(good_time, 1)) + 's'
        #     cv2.putText(image, time_string_good, (10, h - 20), font, font_scale, black, font_thickness)
        # else:
        #     time_string_bad = 'Bad Posture Time : ' + str(round(bad_time, 1)) + 's'
        #     cv2.putText(image, time_string_bad, (10, h - 20), font, font_scale, red, font_thickness)

        # If you stay in bad posture for more than 3 minutes (180s) send an alert.
        if bad_time > 180:
            sendWarning()

        # whether send api or not
        if is_sending:
            cv2.putText(image, "sending", (10, h - 20), font, font_scale, black, font_thickness)
        else:
            cv2.putText(image, "stopping", (10, h - 20), font, font_scale, red, font_thickness)

        # Display.
        cv2.imshow('MediaPipe Pose', image)

        # press space key
        if key == 32:
            is_sending = not is_sending

        if is_sending:
            now = datetime.datetime.now()
            file_name: str = f"{now.year}_{now.month}_{now.day}_{now.hour}:{now.minute}:{now.second}.{now.microsecond}"
            cv2.imwrite(f"images/{user['id']}/{file_name}.jpeg", image)
            post(neck_inclination, torso_inclination, now)
        if key & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
