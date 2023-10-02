import cv2
import numpy as np
import math
import torch
import sys
from typing import Dict
import copy
import random
import string

from config.env import image_dir

_image_dir = image_dir if image_dir is not None else "images"

Point = Dict[str, float]
# x: x_coord
# y: y_coord
# score: score

sys.path.append("pytorch-openpose")
from src.body import Body
from src import util
body_estimation = Body("pytorch-openpose/model/body_pose_model.pth")

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
        print("nose or neck or eyes cannot detected")
        return None
    
    nose: Point = parse_point(candidate[nose_index])
    neck: Point = parse_point(candidate[neck_index])
    right_eye: Point = parse_point(candidate[right_eye_index])
    left_eye: Point = parse_point(candidate[left_eye_index])
    # _subset: np.ndarray = np.array([[s if i < 2 else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    # _subset: np.ndarray = np.array([[s if (i < 2 or i > 17) else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    canvas: np.ndarray = copy.deepcopy(img)
    canvas = util.draw_bodypose(canvas, candidate, subset)
    cv2.imwrite(f"{_image_dir}/neck/{nose['score']}_{neck['score']}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    if nose["score"] < 0.5 or \
        neck["score"] < 0.1 or \
        right_eye["score"] < 0.4 or \
        left_eye["score"] < 0.4:
        print(f"nose: {nose['score']}, neck: {neck['score']}, right eye: {right_eye['score']}, {left_eye['score']}")
        return None

    neck_to_nose: float = math.dist([nose["x"], nose["y"]], [neck["x"], neck["y"]])
    standard_dist: float = math.dist([right_eye["x"], right_eye["y"]], [left_eye["x"], left_eye["y"]])
    return {
        "nose_x": nose["x"],
        "nose_y": nose["y"],
        "neck_to_nose": float(neck_to_nose),
        "standard_dist": float(standard_dist)
    }