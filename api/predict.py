import torch
import numpy as np
import requests
import os

from utils import load_data_from_csvs, parse_torch

API_URL = "http://localhost:8000"
def fetch_data_from_api():
    get_data = requests.get(f"{API_URL}/all-feature/")
    get_data.raise_for_status()
    data = get_data.json()
    x = []
    y = []
    for d in data:
        x_, y_ = parse_torch(d)
        x.extend(x_)
        y.extend(y_)
    return x, y

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

if __name__ == "__main__":
    torch.device("mps")
    # x, y = fetch_data_from_api()
    x, y = load_data_from_csvs()
    x = torch.from_numpy(x).float()
    y = torch.from_numpy(y).float()
    x = torch.stack([torch.ones(100), x], 1)

    # パラメータ
    input_size  = len(x[0])     # 説明変数の数
    output_size = 1     # 推論値の数
    alpha       = 0.01  # 学習率
    epochs      = 1000  # 学習回数

    net, losses = linear_regression(dimension=input_size, out_features=output_size, iteration=epochs, lr=alpha, x=x, y=y)