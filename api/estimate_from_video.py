import os
import sys
from typing import List
import asyncio
import re
import cv2
import datetime

from estimation.internal_posture import update_estimation_from_time

user_id_reg = re.compile(r"\d+")
video_reg = re.compile(r".(mp4|webm)")

targets = sys.argv[1:]

if __name__ == "__main__":
    for user_id in os.listdir("images/") if len(targets) <= 0 else targets:
        if not user_id_reg.search(user_id):
            continue
        dir_path = f"images/{user_id}/original"
        file_names = list(filter(lambda x: video_reg.search(x), os.listdir(dir_path)))
        for file_name in file_names:
            cap = cv2.VideoCapture(os.path.join(dir_path, file_name))
            fps = cap.get(cv2.CAP_PROP_FPS)
            micspf: int = int(10 ** 6 / fps)
            no_extention: str = ".".join(file_name.split(".")[:-1])
            start_time: datetime.datetime = datetime.datetime.strptime(f"{no_extention}000", "%Y-%m-%d_%H:%M:%S.%f")
            count: int = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                count += 1
                now: datetime.datetime = start_time + datetime.timedelta(microseconds = micspf*count)
                file_name: str = now.strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3] + ".jpg"
                cv2.imwrite(os.path.join(dir_path, file_name), frame)
                loop = asyncio.get_event_loop()
                loop.run_until_complete(update_estimation_from_time(dir_path, now.strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3]))
                print("done")