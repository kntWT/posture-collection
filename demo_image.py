import cv2
import numpy as np
import math
import torch
import sys
import os
from typing import List, Dict

Point = Dict[str, float]
# x: x_coord
# y: y_coord
# score: score

path_pytorch_openpose: str = "pytorch-openpose"

sys.path.append(f"{os.getcwd()}/{path_pytorch_openpose}")
from src.body import Body

body_estimation = Body(f"{path_pytorch_openpose}/model/body_pose_model.pth")

# デバイス取得
torch.device("mps")

oriImg = cv2.imread(f"{path_pytorch_openpose}/images/{sys.argv[1]}")
if oriImg is None:
    raise ValueError(f"the file {sys.argv[1]} could not open")

candidate, subset = body_estimation(oriImg)

def parse_point(cand) -> Point:
    return {
        "x": cand[0],
        "y": cand[1],
        "score": cand[2],
    }

nose: Point = parse_point(candidate[0])
neck: Point = parse_point(candidate[1])
print(math.dist([nose["x"], nose["y"]], [neck["x"], neck["y"]]))
