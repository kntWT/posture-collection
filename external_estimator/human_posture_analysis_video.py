import cv2
import time
import math as m
import mediapipe as mp
import os
import datetime

from service import login, calibrate
from util import calculate_posture

NECK_ANGLE_OFFSET: float = 0
user = {}
is_sending: bool = False
set_id: int = 1
max_set_id: int = 5
p_time = datetime.datetime.now()

if __name__ == "__main__":
    user = login()
    os.makedirs(f"images/{user['id']}/original", exist_ok=True)
    os.makedirs(f"images/{user['id']}/neck", exist_ok=True)
    cap = cv2.VideoCapture(0)
    cap.set(3, 2000)
    cap.set(4, 2000)

    # Meta.
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Video writer.
    video_output = None

    while cap.isOpened():
        # Capture frames.
        ret, image = cap.read()
        if not ret:
            continue
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        key = cv2.waitKey(1)
        # print((datetime.datetime.now() - p_time).microseconds / 1000)
        # press left arrow key
        if key == 81:
            set_id -= 1 if set_id >= 1 else 0
        # press right arrow key
        if key == 83:
            set_id += 1 if set_id < max_set_id else 0
        # press space key
        if key == 32:
            is_sending = not is_sending
            if is_sending:
                now = datetime.datetime.now()
                file_name: str = now.strftime("%Y-%m-%d_%H:%M:%S.%f")
                print(file_name)
                video_output = cv2.VideoWriter(f"images/{user['id']}/original/{file_name}.mp4", fourcc, fps, frame_size)
            else:
                print("stop")
        if is_sending:
            video_output.write(image)
        else:
            result = calculate_posture(image, NECK_ANGLE_OFFSET)
            if result is None:
                continue
            image, neck_angle, torso_angle = result
            # press enter key
            if key == 13:
                NECK_ANGLE_OFFSET = neck_angle
                calibrate(neck_angle)
        # Display.
        cv2.imshow('MediaPipe Pose', image)
        if key & 0xFF == ord('q'):
            break

cap.release()
video_output.release()
cv2.destroyAllWindows()
