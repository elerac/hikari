"""
プロジェクタ&カメラを動かす．
例として，Nayarらの高周波照明を投影して，直接成分と大域成分を分離する．
"""
# 外部モジュール
import cv2
import numpy as np
# 自作ソフトウェア関連
import structuredlight as sl
# 自作ハードウェア関連
import PySpin
import EasyPySpin
from fullscreen import FullScreen

def main():
    # カメラの設定
    cap = EasyPySpin.VideoCapture(0)
    #cap.set(cv2.CAP_PROP_GAMMA, 1.0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 3000)
    cap.set(cv2.CAP_PROP_GAIN, 0.0)
    cap.set(cv2.CAP_PROP_FPS, 30)
   
    # プロジェクタの設定
    projector = FullScreen(1)
    width_prj  = projector.width
    height_prj = projector.height
    img_black = np.full((width_prj, height_prj), 0, dtype=np.uint8)
    projector.imshow(img_black)

    # 構造化光の設定
    stlight = sl.Checker(sqsize=10, step=2)
    imlist_pattern = stlight.generate((width_prj, height_prj))
    num = len(imlist_pattern)
    
    # 環境光を除去する
    cv2.waitKey(200)
    ret, frame_black = cap.read()

    imlist_captured = []
    for i, pattern in enumerate(imlist_pattern):
        print("{}/{}".format(i+1, num))
        projector.imshow(pattern)
        cv2.waitKey(200)

        ret, frame = cap.read()
        imlist_captured.append(frame)

    img_direct, img_global = stlight.decode(imlist_captured)
    cv2.imwrite("direct.png", img_direct.astype(np.uint8))
    cv2.imwrite("global.png", img_global.astype(np.uint8))

    cap.release()
    projector.destroyWindow()

if __name__=="__main__":
    main()
