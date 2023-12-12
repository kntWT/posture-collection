import cv2
from pydantic import BaseModel
import numpy as np
import torch
import pandas as pd
from typing import Any, NoReturn, List, Dict
import os
import json
import requests
import asyncio

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

def fetch_data_and_to_csv(url: str, file_name: str):
    get_data = requests.get(url)
    get_data.raise_for_status()
    data = get_data.json()
    to_csv(data, file_name)
    return data

def to_csv(data: List[Dict], file_name: str):
    if len(data) <= 0:
        return
    dir: str = "/".join(file_name.split("/")[:-1])
    os.makedirs(dir, exist_ok=True)
    header = ",".join(data[0].keys())
    lines = [header]
    for d in data:
        line = ",".join([str(v) for v in d.values()])
        lines.append(line)
    with open(file_name, mode="w") as f:
        f.write("\n".join(lines))

def to_flat(arr):
    ret_arr = []
    for v in arr:
        ret_arr.extend(v)
    return ret_arr
