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
from config.env import image_dir


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

async def calc_neck_dist(img: np.ndarray = None) -> float:
    if img is None:
        return -1
    candidate, subset = body_estimation(img)
    if len(subset) <= 0:
        print("cannot detected")
        return -1
    
    nose_index: int = int(subset[0][0])
    neck_index: int = int(subset[0][1])
    if nose_index == -1 or neck_index == -1:
        print("nose or neck cannot detected")
        return -1
    
    nose: Point = parse_point(candidate[nose_index])
    neck: Point = parse_point(candidate[neck_index])
    # _subset: np.ndarray = np.array([[s if i < 2 else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    # _subset: np.ndarray = np.array([[s if (i < 2 or i > 17) else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    canvas: np.ndarray = copy.deepcopy(img)
    canvas = util.draw_bodypose(canvas, candidate, subset)
    cv2.imwrite(f"images/neck/{nose['score']}_{neck['score']}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    if nose["score"] < 0.5 or neck["score"] < 0.1:
        print(f"nose: {nose['score']}, neck: {neck['score']}")
        return -1

    dist: float = math.dist([nose["x"], nose["y"]], [neck["x"], neck["y"]])
    return dist

async def calc_head_angle(img=None) -> float:
    if img is None:
        return -1
    pitch, yaw, roll = map(lambda x: x[0], head_pose_model.predict(img))
    canvas: np.ndarray = copy.deepcopy(img)
    head_pose_model.draw_axis(canvas, pitch, yaw, roll)
    cv2.imwrite(f"{image_dir}/head/{pitch}_{yaw}_{roll}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    return pitch
    
    