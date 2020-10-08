"""
偏光カメラ(FLIR, BFS-U3-51S5P-C)で撮影した偏光画像をDoLPやAoLPに変換して表示する
"""
# 外部モジュール
import cv2
import numpy as np
# 自作ソフトウェア関連
import polanalyser as pa
# 自作ハードウェア関連
import PySpin
import EasyPySpin

def main():
    # カメラの設定
    cap = EasyPySpin.VideoCapture(0)
    cap.set(cv2.CAP_PROP_GAMMA, 1.0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -1)
    cap.set(cv2.CAP_PROP_GAIN, -1)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # 表示の大きさ調節
    scale = 0.25

    while True:
        ret, frame = cap.read()
        
        # 偏光画像のデモザイキング
        img_demosaiced = pa.demosaicing(frame)

        # ストークスベクトルを求める
        radians = np.array([0, np.pi/4, np.pi/2, np.pi*3/4])
        img_stokes = pa.calcStokes(img_demosaiced, radians)
        
        img_stokes = cv2.resize(img_stokes, None, fx=scale, fy=scale)
        
        # ストークスベクトルから値を変換する
        img_intensity = pa.cvtStokesToIntensity(img_stokes)
        img_DoLP      = pa.cvtStokesToDoLP(img_stokes)
        img_AoLP      = pa.cvtStokesToAoLP(img_stokes)
        
        # 正規化する
        img_intensity_norm = np.clip( 255.0*((img_intensity/255.0)**(1/2.2)), 0, 255).astype(np.uint8)
        img_DoLP_norm = np.clip(255.0*img_DoLP, 0, 255).astype(np.uint8)
        img_AoLP_norm = pa.applyColorToAoLP(img_AoLP)
        
        # 撮影画像の表示
        cv2.imshow("intensity", img_intensity_norm)
        cv2.imshow("DoLP", img_DoLP_norm)
        cv2.imshow("AoLP", img_AoLP_norm)
        key = cv2.waitKey(30)
        if key==ord("q"):
            break   

    cap.release()

if __name__=="__main__":
    main()
