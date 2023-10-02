import sys
import requests
from requests.exceptions import HTTPError
import asyncio
import json
from typing import List, Any
import cv2

from config.env import original_image_dir
from estimation.body_pose import calc_neck_dist
from estimation.head_pose import calc_head_angle

API_URL = "http://localhost:4201"

_original_image_dir: str = original_image_dir if original_image_dir is not None else "images/original"
    
async def update_estimation(file_name: str):
    id: int = -1
    try:
        get_row = requests.get(f"{API_URL}/internal-posture/filename/{file_name}")
        get_row.raise_for_status()
        data = get_row.json()
        id: int = data["id"]
        user_id: int = data["user_id"]
        calibrate_flag: bool = data["calibrate_flag"]
    except HTTPError as e:
        print(e)
        return
    try:
        if id == -1:
            return
        image = cv2.imread(f"{_original_image_dir}/{file_name}")
        tasks: List[Any] = []
        tasks.append(calc_neck_dist(image))
        tasks.append(calc_head_angle(image))
        face_feature, head_pose = await asyncio.gather(*tasks)
        if face_feature is None or head_pose is None:
            pass
        else:
            put_feature = requests.put(f"{API_URL}/internal-posture/{id}", json.dumps({**face_feature, **head_pose}))
            put_feature.raise_for_status()
            neck_to_nose_standard = face_feature["neck_to_nose"] / face_feature["standard_dist"]
            if calibrate_flag:
                calibrate_user = requests.put(
                    f"{API_URL}/user/calibration/internal-posture/{user_id}",
                    json.dumps({"neck_to_nose_standard": neck_to_nose_standard})
                )
                calibrate_user.raise_for_status()
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    update_estimation(sys.argv[1])