### arucoマーカーを生成して、画像として保存する
import cv2
from cv2 import aruco
import os
import sys

### --- parameter --- ###

# マーカーの保存先
os.makedirs("markers", exist_ok=True)
dir_mark = "markers"

# 生成するマーカー用のパラメータ
num_mark = 3 #個数
size_mark = 500 #マーカーのサイズ

### --- マーカーを生成して保存する --- ###
# マーカー種類を呼び出し
dict_aruco = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

if __name__ == "__main__":
    for count in range(num_mark) :
        id_mark = count #countをidとして流用
        img_mark = aruco.generateImageMarker(dict_aruco, id_mark, size_mark)

        if count < 10 :
            img_name_mark = 'mark_id_0' + str(count) + '.jpg'
        else :
            img_name_mark = 'mark_id_' + str(count) + '.jpg'
        path_mark = os.path.join(dir_mark, img_name_mark)

        cv2.imwrite(path_mark, img_mark)
