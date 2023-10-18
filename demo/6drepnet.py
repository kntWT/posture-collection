# import time
# import math
# import re
# import sys
import os
from typing import Dict
import string
import random

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import numpy as np
# from numpy.lib.function_base import _quantile_unchecked
import cv2
import torch
# import torch.nn as nn
# from torch.utils.data import DataLoader
from torch.backends import cudnn
# import torch.nn.functional as F
# import torchvision
from torchvision import transforms
from face_detection import RetinaFace
# import matplotlib
# from matplotlib import pyplot as plt
from PIL import Image
# matplotlib.use('TkAgg')


from huggingface_hub import hf_hub_download

from sixdrepnet.model import SixDRepNet
from sixdrepnet import utils

transformations = transforms.Compose([transforms.Resize(224),
                                      transforms.CenterCrop(224),
                                      transforms.ToTensor(),
                                      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

gpu = 0
cam = 0
cudnn.enabled = True
if (gpu < 0):
    device = torch.device('cpu')
else:
    # device = torch.device('cuda:%d' % gpu)
    device = torch.device("mps")
snapshot_path = hf_hub_download(repo_id="osanseviero/6DRepNet_300W_LP_AFLW2000", filename="model.pth")
model = SixDRepNet(backbone_name='RepVGG-B1g2',
                    backbone_file='',
                    deploy=True,
                    pretrained=False)

print('Loading data.')

detector = RetinaFace(gpu_id=gpu)

# Load snapshot
saved_state_dict = torch.load(os.path.join(
    snapshot_path), map_location='cpu')

if 'model_state_dict' in saved_state_dict:
    model.load_state_dict(saved_state_dict['model_state_dict'])
else:
    model.load_state_dict(saved_state_dict)
model.to(device)

# Test the Model
model.eval()  # Change model to 'eval' mode (BN uses moving mean/var).

font = cv2.FONT_HERSHEY_SIMPLEX
green = (127, 255, 0)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    while True:
        ret, img = cap.read()
        if img is None:
         continue
    
        faces = sorted(detector(img), key=lambda x: x[2], reverse=True)
        if len(faces) <= 0:
            continue
        box, landmarks, score = faces[0]
        # Print the location of each face in this image
        if score < .95:
            print(f"face cannot detected (score: {score})")
            continue
        x_min = int(box[0])
        y_min = int(box[1])
        x_max = int(box[2])
        y_max = int(box[3])
        bbox_width = abs(x_max - x_min)
        bbox_height = abs(y_max - y_min)

        x_min = max(0, x_min-int(0.2*bbox_height))
        y_min = max(0, y_min-int(0.2*bbox_width))
        x_max = x_max+int(0.2*bbox_height)
        y_max = y_max+int(0.2*bbox_width)

        canvas = img[y_min:y_max, x_min:x_max]
        canvas = Image.fromarray(canvas)
        canvas = canvas.convert('RGB')
        canvas = transformations(canvas)

        canvas = torch.Tensor(canvas[None, :]).to(device)

        R_pred = model(canvas)

        euler = utils.compute_euler_angles_from_rotation_matrices(
            R_pred)*180/np.pi
        pitch, yaw, roll = euler[0]
        # p_pred_deg = euler[:, 0].cpu()
        # y_pred_deg = euler[:, 1].cpu()
        # r_pred_deg = euler[:, 2].cpu()

        #utils.draw_axis(frame, y_pred_deg, p_pred_deg, r_pred_deg, left+int(.5*(right-left)), top, size=100)
        utils.plot_pose_cube(img,  yaw, pitch, roll, x_min + int(.5*(
            x_max-x_min)), y_min + int(.5*(y_max-y_min)), size=bbox_width)
        # cv2.imwrite(f"{_image_dir}/head/{file_name}.jpg", img)

        cv2.putText(img, f"pitch: {pitch}", (10, 30), font, 0.9, green, 2)
        cv2.putText(img, f"yaw: {yaw}", (10, 60), font, 0.9, green, 2)
        cv2.putText(img, f"roll: {roll}", (10, 90), font, 0.9, green, 2)

        cv2.imshow('sixdrepnet_demo', img)#一个窗口用以显示原视频
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()