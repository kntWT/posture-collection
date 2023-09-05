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
import asyncio
from sixdrepnet import SixDRepNet

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

oriImg = cv2.imread(f"{path_pytorch_openpose}/images/demo.jpg")
if oriImg is None:
    raise ValueError(f"the file {sys.argv[1]} could not open")

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
    # if nose["score"] < 0.5 or neck["score"] < 0.1:
    #     print(f"nose: {nose['score']}, neck: {neck['score']}")
    # _subset: np.ndarray = np.array([[s if (i < 2 or i > 17) else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    _subset: np.ndarray = np.array([[s if i < 2 else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    canvas: np.ndarray = copy.deepcopy(img)
    canvas = util.draw_bodypose(canvas, candidate, _subset)
    cv2.imwrite(f"images/neck/{nose['score']}_{neck['score']}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    # return -1

    dist: float = math.dist([nose["x"], nose["y"]], [neck["x"], neck["y"]])
    return dist

async def calc_head_angle(img=None) -> float:
    if img is None:
        return -1
    pitch, yaw, roll = map(lambda x: x[0], head_pose_model.predict(img))
    canvas: np.ndarray = copy.deepcopy(img)
    head_pose_model.draw_axis(canvas, pitch, yaw, roll)
    cv2.imwrite(f"images/head/{pitch}_{yaw}_{roll}_{''.join(random.choices(string.ascii_uppercase +string.digits, k=10))}.jpg", canvas)
    return pitch
    
def save_file(file) -> str:
    file_name: str = f"images/original/{file.filename.replace(' ','-').replace('/', '-')}"
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()
    return file_name

def remove_file(file_name: str) -> NoReturn:
    try:
        os.remove(file_name)
    except FileNotFoundError:
        print(f"the file {file_name} does not exist")
    return
    