import cv2
import mediapipe as mp
import os
import datetime

from service import login, post, calibrate
from util import calculate_posture, font, font_scale, font_thickness, black, red

NECK_ANGLE_OFFSET: float = 0
user = {}
is_sending: bool = False
set_id: int = 1
max_set_id: int = 5
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
        _, h = image.shape[:2]
        # whether send api or not
        if is_sending:
            cv2.putText(image, "sending", (10, h - 20), font, font_scale, black, font_thickness)
        else:
            cv2.putText(image, "stopping", (10, h - 20), font, font_scale, red, font_thickness)

        result = calculate_posture(image, NECK_ANGLE_OFFSET)
        if result is None:
            continue
        image, neck_inclination, torso_angle = result

        key = cv2.waitKey(1)
        # press space key
        if key == 32:
            is_sending = not is_sending
        # press left arrow key
        elif key == 81:
            set_id -= 1 if set_id >= 1 else 0
        # press right arrow key
        elif key == 83:
            set_id += 1 if set_id < max_set_id else 0
        # press enter key
        elif key == 13:
            NECK_ANGLE_OFFSET = neck_inclination
            calibrate(neck_inclination)
        neck_angle = neck_inclination - NECK_ANGLE_OFFSET

        # Display.
        cv2.imshow('MediaPipe Pose', image)

        if is_sending:
            now = datetime.datetime.now()
            file_name: str = f"{now.year}_{now.month}_{now.day}_{now.hour}:{now.minute}:{now.second}.{now.microsecond}"[:-3]
            cv2.imwrite(f"images/{user['id']}/{file_name}.jpg", image)
            post(user['id'], neck_angle, torso_angle, now)
        if key & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
