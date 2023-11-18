import cv2
import os
import sys
import datetime
import re

from service import post
from util import calculate_posture

user_id_reg = re.compile(r"\d+")
video_reg = re.compile(r".(mp4|webm)")

targets = sys.argv[1:]

if __name__ == "__main__":
    for user_id in os.listdir("images/") if len(targets) <= 0 else targets:
        if not user_id_reg.search(user_id):
            continue
        src_dir_path = f"images/{user_id}/original"
        dist_dir_path = f"images/{user_id}/neck"
        file_names = list(filter(lambda x: video_reg.search(x), os.listdir(src_dir_path)))
        for file_name in file_names:
            cap = cv2.VideoCapture(os.path.join(src_dir_path, file_name))
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(fps)
            micspf: int = int(10 ** 6 / fps)
            no_extention: str = ".".join(file_name.split(".")[:-1])
            start_time: datetime.datetime = datetime.datetime.strptime(f"{no_extention}", "%Y-%m-%d_%H:%M:%S.%f")
            count: int = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                count += 1
                now: datetime.datetime = start_time + datetime.timedelta(microseconds = micspf*count)
                file_name: str = now.strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3] + ".jpg"
                cv2.imwrite(os.path.join(src_dir_path, file_name), frame)
                result = calculate_posture(frame)
                if result is None:
                    continue
                image, neck_angle, torso_angle = result
                cv2.imwrite(os.path.join(dist_dir_path, file_name), image)
                post(int(user_id), neck_angle, torso_angle, now)
                print("done")