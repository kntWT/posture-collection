import os
import sys
import requests
from requests.exceptions import HTTPError
import cv2
import asyncio
import json
from typing import List, Dict, Any, NoReturn
import numpy as np
import datetime

from config.env import original_image_dir
from estimation.body_pose import estimate_body_pose
from estimation.head_pose import estimate_head_pose

API_URL: str = "http://localhost:4201"
    
async def update_estimation(path: str, file_name: str):
    data = fetch_data_from_filename(file_name)
    id = int(data["id"])
    user_id = int(data["user_id"])
    calibrate_flag = data["calibrate_flag"]
    try:
        if id == -1:
            return
        print(f"{id}({file_name})", end=": ")
        image = cv2.imread(os.path.join(path, file_name))
        face_feature, head_pose = await estimate_from_image(image, user_id, file_name)
        put_estimation(id, user_id, calibrate_flag, face_feature, head_pose)
        
    except FileNotFoundError as e:
        print(e)
        return

async def update_estimation_from_time(dir_path: str, time: str):
    data = fetch_closest_data(time)
    if len(data) <= 0:
        raise FileNotFoundError(f"the matched data with file {time}.mp4 does not exist")
    id = int(data["id"])
    user_id = int(data["user_id"])
    calibrate_flag = data["calibrate_flag"]
    file_name = f"{time}.jpg"
    try:
        if id == -1:
            return
        print(f"{id}({file_name})", end=": ")
        image = cv2.imread(os.path.join(dir_path, file_name))
        face_feature, head_pose = await estimate_from_image(image, user_id, file_name)
        put_estimation(id, user_id, calibrate_flag, face_feature, head_pose)
        update_file_name(id, file_name)
        
    except FileNotFoundError as e:
        print(e)
        return

async def estimate_from_image(image: np.ndarray, user_id: int, file_name: str):
    tasks: List[Any] = []
    tasks.append(estimate_body_pose(image, user_id, file_name))
    tasks.append(estimate_head_pose(image, user_id, file_name))
    return await asyncio.gather(*tasks)

def fetch_data_from_filename(file_name: str) -> Dict:
    try:
        get_row = requests.get(f"{API_URL}/internal-posture/filename/{file_name}")
        get_row.raise_for_status()
        data = get_row.json()
        return data
    except HTTPError as e:
        print(e)
        return {}

def fetch_closest_data(time: str) -> Dict:
    try:
        get_row = requests.get(f"{API_URL}/internal-posture/timestamp/{time}")
        get_row.raise_for_status()
        data = get_row.json()
        return data
    except HTTPError as e:
        print(e)
        return {}
    
def update_file_name(id: int, file_name: str) -> NoReturn:
    try:
        put_row = requests.put(f"{API_URL}/internal-posture/filename/{id}", json.dumps({"file_name": file_name}))
        put_row.raise_for_status()
        return
    except HTTPError as e:
        print(e)
        return

def put_estimation(id: int, user_id: int, calibrate_flag: bool, face_feature: Dict, head_pose: Dict):
    if face_feature is None or head_pose is None:
            pass
    else:
        put_feature = requests.put(f"{API_URL}/internal-posture/{id}", json.dumps({**face_feature, **head_pose}))
        put_feature.raise_for_status()
        if face_feature["neck_to_nose"] is None:
            return
        neck_to_nose_standard = face_feature["neck_to_nose"] / face_feature["standard_dist"]
        if calibrate_flag:
            calibrate_user = requests.put(
                f"{API_URL}/user/calibration/internal-posture/{user_id}",
                json.dumps({
                    "internal_posture_calibration_id": id,
                    "neck_to_nose_standard": neck_to_nose_standard
                })
            )
            calibrate_user.raise_for_status()
    return

if __name__ == "__main__":
    update_estimation(sys.argv[1])