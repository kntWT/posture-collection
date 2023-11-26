import os
import sys
from typing import List, Any
import asyncio
import re
import cv2
import datetime

from estimation.internal_posture import update_estimation_from_time_based_on_fps, update_estimation_from_time_based_on_order

user_id_reg = re.compile(r"\d+")
video_reg = re.compile(r".(mp4|webm)")

targets = sys.argv[1:]

to_complete = []

def get_tasks_from_time_based_on_fps(cap, dir_path: str, file_name: str) -> List[Any]:
    tasks: List[Any] = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = 0
    micspf: int = int(10 ** 6 / fps) # micro seconds per frame
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
        tasks.append(update_estimation_from_time_based_on_fps(dir_path, now.strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3]))
    return tasks

def get_tasks_from_time_based_on_order(cap, dir_path: str, file_name: str) -> List[Any]:
    tasks: List[Any] = []
    file_names: List[str] = [] 
    fps = cap.get(cv2.CAP_PROP_FPS)
    micspf: int = int(10 ** 6 / fps) # micro seconds per frame
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
        file_names.append(file_name)
    tasks.extend(update_estimation_from_time_based_on_order(dir_path, start_time.strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3], file_names))
    return tasks

if __name__ == "__main__":
    for user_id in os.listdir("images/") if len(targets) <= 0 else targets:
        if not user_id_reg.search(user_id):
            continue
        dir_path = f"images/{user_id}/original"
        file_names = list(filter(lambda x: video_reg.search(x), os.listdir(dir_path)))
        for file_name in file_names:
            cap = cv2.VideoCapture(os.path.join(dir_path, file_name))
            # to_complete.extend(get_tasks_from_time_based_on_fps(cap, dir_path, file_name))
            to_complete.extend(get_tasks_from_time_based_on_order(cap, dir_path, file_name))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*to_complete))
        print(f"{user_id} done")