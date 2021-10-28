"""
プロジェクタ&カメラを動かす．
例として，Nayarらの高周波照明を投影して，直接成分と大域成分を分離する．
"""
import cv2
import numpy as np
import os
import structuredlight as sl
import polanalyser as pa
import PySpin
import EasyPySpin
from fullscreen import FullScreen

def main():
    dir_name = "mac_hf5x5"
    os.makedirs(dir_name, exist_ok=True)

    cap = EasyPySpin.VideoCaptureEX(0)
    #cap.set(cv2.CAP_PROP_GAMMA, 1.0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 10000)
    cap.set(cv2.CAP_PROP_GAIN, 0.0)
    cap.average_num = 4
    t_min = 100
    t_max = 200000
    t_min = 1000
    t_max = 40000
    t_ref = 10000
    num = None
   
    # プロジェクタの設定
    projector = FullScreen(1)
    width_prj  = projector.width
    height_prj = projector.height
    projector.imshow(0)

    # 構造化光の設定
    stlight = sl.Checker(sqsize=5, step=1)
    imlist_pattern = stlight.generate((width_prj, height_prj))
    num = len(imlist_pattern)
    
    # 漏れ光を除去用の画像を撮影する
    cv2.waitKey(300)
    #ret, frame_black = cap.read()
    ret, frame_black = cap.readHDR(t_min, t_max, num, t_ref)
    frame_black = pa.cvtStokesToIntensity(pa.demosaicing(frame_black))

    imlist_captured = []
    for i, pattern in enumerate(imlist_pattern):
        print("{}/{}".format(i+1, num))
        projector.imshow(pattern)
        cv2.waitKey(300)

        #ret, frame = cap.read()
        ret, frame = cap.readHDR(t_min, t_max, num, t_ref)
        frame = pa.cvtStokesToIntensity(pa.demosaicing(frame))
        # 漏れ光を除去
        dtype = frame.dtype
        frame = np.abs(frame.astype(np.float64)-frame_black.astype(np.float64)).astype(dtype)
        
        name = f"{dir_name}/{dir_name}_{i+1}.exr"
        cv2.imwrite(name, frame.astype(np.float32))

        imlist_captured.append(frame)

    img_direct, img_global = stlight.decode(imlist_captured)
    #cv2.imwrite(f"{dir_name}/{dir_name}_direct.png", img_direct.astype(np.uint8))
    #cv2.imwrite(f"{dir_name}/{dir_name}_global.png", img_global.astype(np.uint8))
    cv2.imwrite(f"{dir_name}/{dir_name}_direct.exr", img_direct.astype(np.float32))
    cv2.imwrite(f"{dir_name}/{dir_name}_global.exr", img_global.astype(np.float32))

    cap.release()
    projector.destroyWindow()

if __name__=="__main__":
    main()
