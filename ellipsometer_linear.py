"""
直線偏光に限定した，エリプソメトリーで3x3のミュラー行列を獲得する．

撮影環境
    カメラ：偏光カメラ(FLIR, BFS-U3-51S5P-C)
    光源：自動偏光板(ツクモ工学, PWA-100 & シグマ光機, GSC-01)
"""
# 外部モジュール
import cv2
import numpy as np
from math import radians, degrees
# 自作ソフトウェア関連
import polanalyser as pa
# 自作ハードウェア関連
import PySpin
import EasyPySpin
from libs.fullscreen import FullScreen
from autopolarizer import AutoPolarizer

def main():
    # カメラの設定
    cap = EasyPySpin.VideoCaptureEX(0)
    cap.set(cv2.CAP_PROP_GAMMA, 1.0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 10000)
    cap.set(cv2.CAP_PROP_GAIN, 5)
    #cap.set(cv2.CAP_PROP_FPS, 30)
    cap.average_num = 4 # 平均化させる枚数，ノイズ耐性を上げる
    
    # プロジェクタの設定
    projector = FullScreen(1)
    img_white = 255*np.ones((projector.height, projector.width), dtype=np.uint8)
    projector.imshow(img_white)
    cv2.waitKey(100)

    # 光源側の偏光板設定
    polarizer = AutoPolarizer("/dev/tty.usbserial-FTRWB1RN")
    polarizer.set_speed()
    polarizer.reset()
    polarizer.flip_front = True
    
    # 撮影する光源とカメラの偏光板角度の組み合わせ
    # 光源側は自由に設定可能
    # カメラ側は偏光カメラなので固定
    light_angles_sequence  = [0, np.pi/4, np.pi/2, np.pi*3/4]
    camera_angles_sequence = [0, np.pi/4, np.pi/2, np.pi*3/4]
    
    imlist = []
    anglist_light  = []
    anglist_camera = []
    for i, radians in enumerate(light_angles_sequence):
        # 偏光板を回転
        polarizer.degree = degrees(radians)

        print("{0}/{1}: {2}".format(i+1, len(light_angles_sequence), polarizer.degree))

        # 少し待ってから撮影
        cv2.waitKey(100)
        #ret, frame = cap.read()
        ret, frame = cap.readHDR(500, 10000, num=6)
        
        # 偏光画像のデモザイキング
        img_demosaiced = pa.IMX250MZR.demosaicing(frame)

        for img, ang_cam in zip( cv2.split(img_demosaiced), camera_angles_sequence):
            name = "fname_l{0}_c{1}.exr".format(int(degrees(radians)), int(degrees(ang_cam)))
            cv2.imwrite(name, img.astype(np.float32))
        
        # 撮影したの画像と角度情報をリストに追加
        imlist += cv2.split(img_demosaiced)
        anglist_light  += [radians]*4
        anglist_camera += [np.pi-rad for rad in camera_angles_sequence]
    
    cap.release()
    
    # リストをndarray形式に変換
    images = cv2.merge(imlist)
    angles_light  = np.array(anglist_light)
    angles_camera = np.array(anglist_camera)

    # ミュラー行列を求める
    img_mueller = pa.calcMueller(images, angles_light, angles_camera)
    img_m11, img_m12, img_m13,\
    img_m21, img_m22, img_m23,\
    img_m31, img_m32, img_m33  = cv2.split(img_mueller)

    np.save("img_mueller.npy", img_mueller)

if __name__=="__main__":
    main()
