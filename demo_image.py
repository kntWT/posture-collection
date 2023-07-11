import cv2
import numpy as np
import math
import torch
import sys
import os
from typing import List, Dict
from sixdrepnet import SixDRepNet
from src.body import Body

Point = Dict[str, float]
# x: x_coord
# y: y_coord
# score: score

path_pytorch_openpose: str = "pytorch-openpose"
sys.path.append(f"{os.getcwd()}/{path_pytorch_openpose}")
body_estimation = Body(f"{path_pytorch_openpose}/model/body_pose_model.pth")
# デバイス取得
torch.device("mps")

# head_pose_model = SixDRepNet()

def parse_point(cand) -> Point:
    return {
        "x": cand[0],
        "y": cand[1],
        "score": cand[2],
    }

oriImg = cv2.imread(f"{path_pytorch_openpose}/images/demo.jpg")
if oriImg is None:
    raise ValueError(f"the file {sys.argv[1]} could not open")

def calc_neck_dist(img=None) -> float:
    if img is None:
        return -1
    candidate, subset = body_estimation(oriImg)

    nose: Point = parse_point(candidate[0])
    neck: Point = parse_point(candidate[1])
    dist = math.dist([nose["x"], nose["y"]], [neck["x"], neck["y"]])
    return dist

def calc_head_angle(img=None) -> float:
    # pitch, yaw, roll = head_pose_model.predict(oriImg)
    # return pitch
    return 0
    