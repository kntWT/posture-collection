import cv2
from pydantic import BaseModel
import numpy as np
import torch

from typing import Any, NoReturn
import os
import json

import requests

image_dir: str = os.environ.get("IMAGE_DIR")

def save_file(file, path: str = "") -> str:
    dir_path = f"{image_dir}/{path}/original/"
    os.makedirs(dir_path, exist_ok=True)
    file_name = os.path.join(dir_path, file.filename)
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


class JsonParser:
    def __init__(self, model: BaseModel):
        self.model = model

    def __call__(self, json_obj: json):
        dict_obj = json.loads(json_obj)
        return self.model(**dict_obj)

def parse_torch(data):
    neck_to_nose = data["neck_to_nose"]
    standard_dist = data["standard_dist"]
    normalized_dist = neck_to_nose / standard_dist
    neck_to_nose_standard = data["neck_to_nose_standard"]
    normalized_ratio = normalized_dist / neck_to_nose_standard
    alpha = data["orientation_alpha"]
    beta = data["orientation_beta"]
    gamma = data["orientation_gamma"]
    pitch = data["pitch"]
    yaw = data["yaw"]
    roll = data["roll"]
    nose_x = data["nose_x"]
    nose_y = data["nose_y"]
    x = torch.from_numpy(np.array([
        normalized_ratio,
        # alpha,
        beta,
        # gamma,
        pitch,
        # yaw,
        # roll,
        # nose_x,
        # nose_y,
    ])).float()
    neck_angle = data["neck_angle"]
    neck_angle_offset = data["neck_angle_offset"]
    y = torch.from_numpy(np.array([neck_angle - neck_angle_offset])).float()
    return x, y

def load_data_from_csvs(dir: str = "data"):
    x = []
    y = []
    for file_name in os.listdir(dir):
        if not file_name.endswith(".csv"):
            continue
        x_, y_ = load_data_from_csv(f"{dir}/{file_name}")
        x.extend(x_)
        y.extend(y_)
    return x, y

def load_data_from_csv(file_name: str):
    data = []
    with open(file_name) as f:
        lines = f.readlines()
        cols = lines[0].split(",")
        for line in lines[1:]:
            data_list = line.split(",")
            data.append({cols[i] : float(data_list[i]) for i in range(len(cols))})
    
    return parse_torch(data)

def fetch_data_and_to_csv(url: str, file_name: str):
    get_data = requests.get(url)
    get_data.raise_for_status()
    data = get_data.json()
    header = ",".join(data[0].keys())
    lines = [header]
    for d in data:
        line = ",".join([str(v) for v in d.values()])
        lines.append(line)
    with open(file_name, mode="w") as f:
        f.write("\n".join(lines))