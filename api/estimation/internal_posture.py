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

from estimation.body_pose import estimate_body_pose
from estimation.head_pose import estimate_head_pose

API_URL: str = "http://localhost:4201"
    
def update_estimation(path: str, file_name: str):
    data = fetch_data_from_filename(file_name)
    if len(data) <= 0:
        print(f"the matched data with file \"{file_name}\" does not exist")
    else:
        return asyncio.create_task(update_estimation_from_data(data, path, file_name))

def update_estimation_from_time_based_on_fps(dir_path: str, time: str, execute: bool = True):
    data = fetch_closest_data(time)
    if len(data) <= 0:
        print(f"the matched data with file {time}.mp4 does not exist")
    else:
        return asyncio.create_task(update_estimation_from_data(data, dir_path, f"{time}.jpg", execute))

def update_estimation_from_time_based_on_order(dir_path: str, start_time: str, file_names: List[str], execute: bool = True) -> List[Any]:
    frame_count: int = len(file_names)
    data_list: List[Dict] = fetch_data_list_from_start_time(start_time, frame_count)
    tasks: List[Any] = []
    if len(data_list) <= 0 or len(data_list) < frame_count:
        print(f"the matched data with file {start_time}.mp4 does not exist")
        return []
    for data, file_name in zip(data_list, file_names):
        task = asyncio.create_task(update_estimation_from_data(data, dir_path, file_name, execute))
        tasks.append(task)
    return tasks
        
async def update_estimation_from_data(data: Dict, dir_path: str, file_name: str, execute: bool = True):
    id = int(data["id"])
    user_id = int(data["user_id"])
    calibrate_flag = data["calibrate_flag"]
    try:
        if id == -1:
            return
        print(f"{id}({file_name})", end=": ")
        image = cv2.imread(os.path.join(dir_path, file_name))
        face_feature, head_pose = await estimate_from_image(image, user_id, file_name)
        if face_feature is None or head_pose is None:
            return
        to_put_estimation = put_estimation(id, user_id, calibrate_flag, face_feature, head_pose, execute)
        to_put_file_name = put_file_name(id, file_name, execute)
        print("done")

        if execute:
            return
        else:
            to_put_estimation.update(to_put_file_name)
            return to_put_estimation
        
    except FileNotFoundError as e:
        print(e)
        return

async def estimate_from_image(image: np.ndarray, user_id: int, file_name: str):
    # tasks: List[Any] = []
    # tasks.append(estimate_body_pose(image, user_id, file_name))
    # tasks.append(estimate_head_pose(image, user_id, file_name))
    # return await asyncio.gather(*tasks)
    face_feature = await estimate_body_pose(image, user_id, file_name)
    head_pose = await estimate_head_pose(image, user_id, file_name)
    return face_feature, head_pose

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
        if data["file_name"] is not None:
            current_time: datetime.datetime = datetime.datetime.strptime(time+"000", "%Y-%m-%d_%H:%M:%S.%f")
            matched_time: datetime.datetime = datetime.datetime.strptime(data["file_name"][:-4]+"000", "%Y-%m-%d_%H:%M:%S.%f")
            data_time: datetime.datetime = datetime.datetime.strptime(data["created_at"], "%Y-%m-%d_%H:%M:%S.%f")
            if abs((current_time-data_time).total_seconds()) >= abs((matched_time-data_time).total_seconds()):
                return {}

        return data
    except HTTPError as e:
        print(e)
        return {}

def fetch_data_list_from_start_time(start_time: str, frame_count) -> List[Dict]:
    try:
        get_row = requests.get(f"{API_URL}/internal-posture/timestamp/list/{start_time}/{frame_count}")
        get_row.raise_for_status()
        data = get_row.json()
        return data
    except HTTPError as e:
        print(e)
        return []
    
def put_file_name(id: int, file_name: str, execute: bool = True) -> NoReturn:
    if not execute:
        return {"file_name": {"id": id, "file_name": file_name}}

    try:
        put_row = requests.put(f"{API_URL}/internal-posture/filename/{id}", json.dumps({"id": id, "file_name": file_name}))
        put_row.raise_for_status()
        return
    except HTTPError as e:
        print(e)
        return

def put_estimation(id: int, user_id: int, calibrate_flag: bool, face_feature: Dict, head_pose: Dict, execute: bool = True):
    if face_feature is None or head_pose is None:
        return
    
    if not execute:
        calibration = None if not calibrate_flag or face_feature["neck_to_nose"] is None \
            else {"id": user_id, "internal_posture_calibration_id": id, "neck_to_nose_standard": face_feature["neck_to_nose"] / face_feature["standard_dist"]}
        return {
            "internal_posture": {"id": id, **face_feature, **head_pose},
            "calibration":calibration
        } if calibration is not None else {"internal_posture": {"id": id, **face_feature, **head_pose}}
    
    put_feature = requests.put(f"{API_URL}/internal-posture/{id}", json.dumps({"id": id, **face_feature, **head_pose}))
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

if __name__ == "__main__":
    update_estimation(sys.argv[1])