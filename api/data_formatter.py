import datetime
import numpy as np
import torch
import pandas as pd
import os
import re
from random import sample
from scipy.spatial.transform import Rotation

from helpers import to_csv, to_flat

def load_data_from_csvs(dir: str = "data", mode: str = "torch", filter_reg = re.compile(r".\.csv"), remove_reg = None):
    x = None
    y = None
    for file_name in os.listdir(dir):
        if not file_name.endswith(".csv"):
            continue
        elif not filter_reg.search(file_name):
            continue
        elif remove_reg is not None and remove_reg.search(file_name):
            continue

        x_, y_ = load_data_from_csv(f"{dir}/{file_name}", mode)
        # x.extend(x_)
        # y.extend(y_)
        if x is None or y is None:
            x = x_
            y = y_
        else:
            if mode == "torch":
                x = torch.cat((x, x_), 0)
                y = torch.cat((y, y_), 0)
            elif mode == "np" or mode == "numpy":
                # print(x.shape, x_.shape)
                x = np.concatenate((x, x_), axis=1)
                # print(y.shape, y_.shape)
                y = np.concatenate((y, y_))
            elif mode == "pd" or mode == "pandas":
                x = pd.concat([x, x_], ignore_index=True)
                y = pd.concat([y, y_], ignore_index=True)
            else:
                return None
    return x, y

def load_data_from_csv(file_name: str, mode: str = "torch"):
    data = []
    with open(file_name) as f:
        lines = f.readlines()
        cols = lines[0].replace('"', "").replace("\n", "").split(",")
        for line in lines[1:]:
            data_list = line.replace('"', "").replace("\n", "").split(",")
            data.append({cols[i] : data_list[i] for i in range(len(cols))})

    if mode == "torch":
        return parse_torch(data)
    elif mode == "np" or mode == "numpy":
        return parse_np(data)
    elif mode == "pd" or mode == "pandas":
        return parse_pd(data)
    elif mode == "list":
        return try_parse_float(data)
    else:
        return None

def parse_np(data):
    set_id = np.array([float(d["set_id"]) for d in data])
    neck_to_nose = np.array([float(d["neck_to_nose"]) for d in data])
    standard_dist = np.array([float(d["standard_dist"]) for d in data])
    normalized_dist = neck_to_nose / standard_dist
    neck_to_nose_standard = np.array([float(d["neck_to_nose_standard"]) if "neck_to_nose_standard" in d and d["neck_to_nose_standard"] is not None else 2.5 for d in data])
    normalized_ratio = normalized_dist / neck_to_nose_standard
    orientation_alpha = np.array([float(d["orientation_alpha"]) for d in data])
    orientation_beta = np.array([float(d["orientation_beta"]) for d in data])
    orientation_gamma = np.array([float(d["orientation_gamma"]) for d in data])
    rots = np.array([Rotation.from_euler("zyx", [a, b, g], degrees=True).as_euler("yxz", degrees=True) for a, b, g in zip(orientation_alpha, orientation_beta, orientation_gamma)])
    beta = rots[:, 0]
    gamma = rots[:, 1]
    alpha = rots[:, 2]
    pitch = np.array([float(d["pitch"]) for d in data])
    yaw = np.array([float(d["yaw"]) for d in data])
    roll = np.array([float(d["roll"]) for d in data])
    nose_x = np.array([float(d["nose_x"]) for d in data])
    nose_y = np.array([float(d["nose_y"]) for d in data])

    neck_angle = np.array([float(d["neck_angle"] if "neck_angle" in d else 0) for d in data])
    neck_angle_offset = np.array([float(d["neck_angle_offset"] if "neck_angle_offset" in d else 0) for d in data])

    thres = 15
    def filter(i):
      return beta[i] <= 100 and \
                beta[i] >= -10 and \
                abs(pitch[i]) <= 100 \
                #  abs(alpha[i]) <= thres and \
                #  abs(gamma[i]) <= thres and \
                #  abs(yaw[i]) <= thres and \
                #  abs(roll[i]) <= thres and \
    x_ = []
    y_ = []
    for i in range(len(data)):
        if filter(i):
            x_.append(np.array([
                # set_id[i],
                normalized_ratio[i],
                # alpha[i],
                beta[i],
                # gamma[i],
                # math.sin(pitch[i]),
                pitch[i]
                # yaw[i],
                # roll[i],
                # nose_x[i],
                # nose_y[i],
            ]))
        y_.append(np.array(neck_angle[i] - neck_angle_offset[i]))
    x = np.array(x_).T
    y = np.array(y_)
    return x, y

def parse_torch(data):
    x_, y_ = parse_np(data)
    return parse_torch_from_np(x_, y_)

def parse_torch_from_np(x_, y_):
    x = torch.from_numpy(x_).float()
    y = torch.from_numpy(y_).float()
    return x, y

def parse_pd(data):
    x_, y_ = parse_np(data)
    return parse_pd_from_np(x_, y_)

def parse_pd_from_np(x_, y_):
    col_n, row_n = x_.shape
    x = pd.DataFrame(data=x_.T, columns=[i for i in range(col_n)])
    y = pd.DataFrame(data=y_.T, columns=[0])
    return x, y

def try_parse_float(data):
    ret_data = []
    for _d in data:
        d = {}
        for key, value in _d.items():
            try:
                d[key] = float(value)
            except ValueError:
                d[key] = value
        ret_data.append(d)
    return ret_data

def join_data_with_timestamp(left_table, right_table, split_num: int = 5, threshold: int = 40):
    joined_table = [[] for _ in range(split_num)]
    if len(left_table) <= 0 or len(right_table) <= 0:
        return joined_table
    left_index: int = 0
    right_index: int = 0
    pre_timediff: int = None # micro sec
    pre_row: dict = None
    while True:
        if left_index >= len(left_table) or right_index >= len(right_table):
            break
        # if left_index + right_index > 200:
        #   break
        left_row = left_table[left_index]
        right_row = right_table[right_index]
        left_time = datetime.datetime.strptime(left_row["created_at"], '%Y-%m-%d_%H:%M:%S.%f')
        right_time = datetime.datetime.strptime(right_row["created_at"], '%Y-%m-%d_%H:%M:%S.%f')
        timediff = (left_time - right_time).total_seconds() * 1000
        if pre_timediff is None:
            pre_timediff = timediff
        if abs(timediff) > threshold:
            if pre_row is not None:
              right_row["ex_id"] = right_row.pop("id")
              right_row.pop("user_id")
              right_row["ex_created_at"] = right_row.pop("created_at")
              set_id = int(left_row["set_id"]) - 1
              if set_id < split_num:
                joined_table[set_id].append(dict(**pre_row, **right_row))
                # joined_table[int(left_row["set_id"]) - 1].append([dict(**pre_row), dict(**right_row)])
                pre_row = None
              right_index += 1
            if timediff < 0:
              left_index += 1
            elif timediff > 0:
              right_index += 1
            continue

        if pre_row is None:
            pre_row = left_row
            left_index += 1
            continue
        if abs(timediff) < abs(pre_timediff):
            pre_row = left_row
            left_index += 1
        else:
            right_row["ex_id"] = right_row.pop("id")
            right_row.pop("user_id")
            right_row["ex_created_at"] = right_row.pop("created_at")
            set_id = int(left_row["set_id"]) - 1
            if set_id < split_num:
              joined_table[set_id].append(dict(**pre_row, **right_row))
              # joined_table[int(left_row["set_id"]) - 1].append([dict(**pre_row), dict(**right_row)])
              pre_row = None
            right_index += 1
        pre_timediff = timediff

    return joined_table

def load_data_from_separated_csv(user_id: int, dir="./", export=True):
    internal_postures = load_data_from_csv(os.path.join(dir, f"{user_id}_internal_postures.csv"), "list")
    external_postures = load_data_from_csv(os.path.join(dir, f"{user_id}_external_postures.csv"), "list") # joined with users
    joined = join_data_with_timestamp(internal_postures, external_postures)
    if export:
        to_csv(to_flat(joined), os.path.join(dir, f"{user_id}_all_feature.csv"))
    joined_np = np.stack([parse_np(data) for data in joined])
    return joined_np

def split_data(data, split_num: int = 5):
    data_list = [[] for _ in range(split_num)]
    for d in data:
        set_id = int(d["set_id"]) - 1
        if set_id < 0 or set_id >= split_num:
            continue
        data_list[set_id].append(d)
  
    return data_list

# concatenate list of personal data
# personal data: [section][data_list][data_type]
# returns [section][data_type][data] as numpy array
def concat_data(data_list):
    row_nums = [sum([d[i][0].shape[1] for d in data_list]) for i in range(len(data_list[0]))]
    data = [np.array([np.empty((3, row_nums[i])), np.empty((row_nums[i], ))]) for i in range(len(data_list[0]))]
    for i in range(len(data_list[0])):
        for j in range(len(data_list[0][i])):
            axis = 1 if len(data_list[0][i][j].shape) > 1 else 0
            data[i][j] = np.concatenate([d[i][j] for d in data_list], axis=axis)
    return np.array(data)

# input: [section][data_type][data] as numpy array
def resample_to_equal_size(data_list: np.ndarray, group_range=(0, 60, 10)):
    grouped = [[[] for _ in range(*group_range)] for i in range(data_list.shape[0])]
    for i, data in enumerate(data_list):
        for d in data[1]:
            y = int(d/group_range[2]) 
            grouped[i][y].append(d)
    
    min_size_by_section = [min([len(g) for g in grouped[i]]) for i in range(len(grouped))]
    min_size = min(min_size_by_section)
    balanced = [[] for _ in range(data_list.shape[0])]
    for i, group in enumerate(grouped):
        for g in group:
            balanced[i].extend(sample(g, min_size))
    
    return np.array(balanced)