import cv2
import mediapipe as mp
import os
import datetime

from service import login, post, post_list, calibrate
from util import calculate_posture, font, font_scale, font_thickness, black, red

NECK_ANGLE_OFFSET: float = 0
user = {}
is_sending: bool = False
set_id: int = 1
max_set_id: int = 6
postures = []
# ===============================================================================================#


if __name__ == "__main__":
    user = login()
    NECK_ANGLE_OFFSET = float(user['neck_angle_offset'])
    print(f"NECK_ANGLE_OFFSET: {NECK_ANGLE_OFFSET}")
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
            cv2.putText(image, "recording", (10, h - 20), font, font_scale, black, font_thickness)
        else:
            if len(postures) > 0:
                cv2.putText(image, "posting", (10, h - 20), font, font_scale, black, font_thickness)
            else:
                cv2.putText(image, "stopping", (10, h - 20), font, font_scale, red, font_thickness)

        result = calculate_posture(image, NECK_ANGLE_OFFSET)
        if result is None:
            continue
        image, neck_angle, torso_angle = result

        key = cv2.waitKey(5)
        # press space key
        if key == 32:
            is_sending = not is_sending and len(postures) == 0
            if not is_sending:
                # for posture in postures:
                    # post(posture['user_id'], posture['neck_angle'], posture['torso_angle'], posture['created_at'])
                post_list(postures)
                postures = []
        # press left arrow key
        elif key == 81:
            set_id -= 1 if set_id >= 1 else 0
        # press right arrow key
        elif key == 83:
            set_id += 1 if set_id < max_set_id else 0
        # press enter key
        elif key == 13:
            NECK_ANGLE_OFFSET = neck_angle
            calibrate(user["id"], neck_angle)
            print(f"NECK_ANGLE_OFFSET: {NECK_ANGLE_OFFSET}")

        # Display.
        cv2.imshow('MediaPipe Pose', image)

        if is_sending:
            now = datetime.datetime.now()
            file_name: str = now.strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3]
            cv2.imwrite(f"images/{user['id']}/{file_name}.jpg", image)
            # post(user['id'], neck_angle, torso_angle, now)
            postures.append({"user_id": user['id'], "neck_angle": neck_angle + NECK_ANGLE_OFFSET, "torso_angle": torso_angle, "created_at": file_name})
        if key & 0xFF == ord('q'):
            break

# for posture in postures:
    # post(posture['user_id'], posture['neck_angle'], posture['torso_angle'], posture['created_at'])
post_list(postures)

cap.release()
cv2.destroyAllWindows()
