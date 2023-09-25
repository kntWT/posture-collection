import torch
from torch import nn
import numpy as np
import requests

API_URL = "http://localhost:8000"

def linear_regression(dimension, out_features, iteration, lr, x, y):
    net = torch.nn.Linear(in_features=dimension, out_features=out_features, bias=False)  # ネットワークに線形結合モデルを設定
    optimizer = torch.optim.SGD(net.parameters(), lr=lr)                      # 最適化にSGDを設定
    E = torch.nn.MSELoss()                                                    # 損失関数にMSEを設定
 
    # 学習ループ
    losses = []
    for i in range(iteration):
        optimizer.zero_grad()                                                 # 勾配情報を0に初期化
        y_pred = net(x)                                                       # 予測
        loss = E(y_pred.reshape(y.shape), y)                                  # 損失を計算(shapeを揃える)
        loss.backward()                                                       # 勾配の計算
        optimizer.step()                                                      # 勾配の更新
        losses.append(loss.item())                                            # 損失値の蓄積
        if i % 100 == 99:
            print(list(net.parameters()), loss.item())
    print(net.weight.data.numpy()[0])
 
    return net, losses

def fetch_data():
    get_data = requests.get(f"{API_URL}/all-feature/")
    get_data.raise_for_status()
    data = get_data.json()
    x = []
    y = []
    for d in data:
        neck_to_nose = d["neck_to_nose"]
        standard_dist = d["standard_dist"]
        normalized_dist = neck_to_nose / standard_dist
        neck_to_nose_standard = d["neck_to_nose_standard"]
        normalized_ratio = normalized_dist / neck_to_nose_standard
        alpha = d["orientation_alpha"]
        beta = d["orientation_beta"]
        gamma = d["orientation_gamma"]
        pitch = d["pitch"]
        yaw = d["yaw"]
        roll = d["roll"]
        nose_x = d["nose_x"]
        nose_y = d["nose_y"]
        x.append([
            normalized_ratio,
            alpha,
            beta,
            gamma,
            pitch,
            yaw,
            roll,
            # nose_x,
            # nose_y,
        ])
        neck_angle = d["neck_angle"]
        neck_angle_offset = d["neck_angle_offset"]
        y.append([neck_angle - neck_angle_offset])
    return x, y

if __name__ == "__main__":
    x, y = fetch_data()
    x = torch.from_numpy(x).float()
    y = torch.from_numpy(y).float()
    x = torch.stack([torch.ones(100), x], 1)

    # パラメータ
    input_size  = len(x[0])     # 説明変数の数
    output_size = 1     # 推論値の数
    alpha       = 0.01  # 学習率
    epochs      = 1000  # 学習回数

    net, losses = linear_regression(dimension=input_size, out_features=output_size, iteration=epochs, lr=alpha, x=x, y=y)