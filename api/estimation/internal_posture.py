import os
import sys
import requests
from requests.exceptions import HTTPError
import cv2
import asyncio
import json
from typing import List, Dict, Any

from config.env import original_image_dir
from estimation.body_pose import estimate_body_pose
from estimation.head_pose import estimate_head_pose

API_URL = "http://localhost:4201"
    
async def update_estimation(path: str, file_name: str):
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
        print(f"{id}({file_name})", end=": ")
        image = cv2.imread(os.path.join(path, file_name))
        tasks: List[Any] = []
        tasks.append(estimate_body_pose(image, user_id, file_name))
        tasks.append(estimate_head_pose(image, user_id, file_name))
        face_feature, head_pose = await asyncio.gather(*tasks)
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
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    update_estimation(sys.argv[1])