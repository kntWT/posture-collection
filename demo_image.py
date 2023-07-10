import cv2
import matplotlib.pyplot as plt
import copy
import numpy as np
import torch
import sys
import os

path_pytorch_openpose: str = "pytorch-openpose"

sys.path.append(f"{os.getcwd()}/{path_pytorch_openpose}")
from src import model
from src import util
from src.body import Body

body_estimation = Body(f"{path_pytorch_openpose}/model/body_pose_model.pth")

# デバイス取得
torch.device("mps")

oriImg = cv2.imread(f"{path_pytorch_openpose}/images/{sys.argv[1]}")
if oriImg is None:
    raise ValueError(f"the file {sys.argv[1]} could not open")

candidate, subset = body_estimation(oriImg)
canvas = copy.deepcopy(oriImg)
canvas = util.draw_bodypose(canvas, candidate, subset)

cv2.namedWindow("result", cv2.WINDOW_NORMAL)
cv2.imshow('result', canvas)#一个窗口用以显示原视频

cv2.waitKey()
cv2.destroyAllWindows()

