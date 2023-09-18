import cv2
import numpy as np
import math
import torch
import sys
import os
from typing import List, Dict, NoReturn
import copy
import random
import string
from sixdrepnet import SixDRepNet
from config.env import image_dir, original_image_dir
import requests
from requests.exceptions import HTTPError

API_URL = "http://localhost:4201"

Point = Dict[str, float]
# x: x_coord
# y: y_coord
# score: score

path_pytorch_openpose: str = "pytorch-openpose"
sys.path.append(f"{os.getcwd()}/{path_pytorch_openpose}")
from src.body import Body
from src import util
body_estimation = Body(f"{path_pytorch_openpose}/model/body_pose_model.pth")

head_pose_model = SixDRepNet()
# デバイス取得
torch.device("mps")

def parse_point(cand) -> Point:
    return {
        "x": cand[0],
        "y": cand[1],
        "score": cand[2],
    }

async def calc_neck_dist(img: np.ndarray = None) -> Dict | None:
    if img is None:
        return None
    candidate, subset = body_estimation(img)
    if len(subset) <= 0:
        print("cannot detected")
        return None
    
    nose_index: int = int(subset[0][0])
    neck_index: int = int(subset[0][1])
    right_eye_index: int = int(subset[0][14])
    left_eye_index: int = int(subset[0][15])
    if nose_index == -1 or neck_index == -1 or right_eye_index == -1 or left_eye_index == -1:
        print("nose or neck cannot detected")
        return None
    
    nose: Point = parse_point(candidate[nose_index])
    neck: Point = parse_point(candidate[neck_index])
    right_eye: Point = parse_point(candidate[right_eye_index])
    left_eye: Point = parse_point(candidate[left_eye_index])
    # _subset: np.ndarray = np.array([[s if i < 2 else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    # _subset: np.ndarray = np.array([[s if (i < 2 or i > 17) else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    canvas: np.ndarray = copy.deepcopy(img)
    canvas = util.draw_bodypose(canvas, candidate, subset)
    cv2.imwrite(f"images/neck/{nose['score']}_{neck['score']}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    if nose["score"] < 0.5 or \
        neck["score"] < 0.1 or \
        right_eye["score"] < 0.4 or \
        left_eye["score"] < 0.4:
        print(f"nose: {nose['score']}, neck: {neck['score']}, right eye: {right_eye['score']}, {left_eye['score']}")
        return None

    neck_to_nose: float = math.dist([nose["x"], nose["y"]], [neck["x"], neck["y"]])
    standard_dist: float = math.dist([right_eye["x"], right_eye["y"]], [left_eye["x"], left_eye["y"]])
    return {
        "neck_to_nose": neck_to_nose,
        "standard_dist": standard_dist
    }

async def calc_head_angle(img=None) -> Dict | None:
    if img is None:
        return None
    pitch, yaw, roll = map(lambda x: x[0], head_pose_model.predict(img))
    canvas: np.ndarray = copy.deepcopy(img)
    head_pose_model.draw_axis(canvas, pitch, yaw, roll)
    cv2.imwrite(f"{image_dir}/head/{pitch}_{yaw}_{roll}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    return {
        "pitch": pitch,
        "yaw": yaw,
        "roll": roll
    }
    
if __name__ == "__main__":
    file_name: str = sys.argv[1]
    id: int = -1
    try:
        get_id = requests.get(f"{API_URL}/internal-posture/filename/{file_name}")
        get_id.raise_for_status()
        id = get_id.json()["id"]
    except HTTPError as e:
        raise e
    try:
        image = cv2.imread(f"{original_image_dir}/{file_name}")
        face_feature = calc_neck_dist(image)
        head_pose = calc_head_angle(image)
        if face_feature is None or head_pose is None:
            pass
        else:
            put_feature = requests.put(f"{API_URL}/internal-posutre/{id}", {**face_feature, **head_pose})
            print(put_feature.json())
    except FileNotFoundError as e:
        print(e)
