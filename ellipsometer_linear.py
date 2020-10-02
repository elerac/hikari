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
import os
# 自作ソフトウェア関連
import polanalyser as pa
# 自作ハードウェア関連
import PySpin
import EasyPySpin
from fullscreen import FullScreen
from autopolarizer import AutoPolarizer

def main():
    # 出力するフォルダ名
    dir_name = "alumi"
    os.makedirs(dir_name, exist_ok=True)

    # カメラの設定
    cap = EasyPySpin.VideoCaptureEX(0)
    #cap.cam.AdcBitDepth.SetValue(PySpin.AdcBitDepth_Bit12)
    #cap.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono16)
    cap.set(cv2.CAP_PROP_GAMMA, 1.0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 10000)
    cap.set(cv2.CAP_PROP_GAIN, 0)
    cap.average_num = 28 # 平均化させる枚数，ノイズ耐性を上げる
    t_min = 8
    t_max = 300000
    t_ref = 30000
    num = 16
    
    # プロジェクタの設定
    projector = FullScreen(1)
    projector.imshow(255)
    cv2.waitKey(600)

    # 光源側の偏光板設定
    polarizer = AutoPolarizer("/dev/tty.usbserial-FTRWB1RN")
    polarizer.set_speed()
    polarizer.reset()
    polarizer.flip_front = False
    
    # 撮影する光源とカメラの偏光板角度の組み合わせ
    # 光源側は自由に設定可能
    # カメラ側は偏光カメラなので固定
    light_angles_sequence  = [0, np.pi/4, np.pi/2, np.pi*3/4]
    camera_angles_sequence = [0, np.pi*3/4, np.pi/2, np.pi/4]
    
    print("Capture start")
    imlist = []
    anglist_light  = []
    anglist_camera = []
    for i, radians_light in enumerate(light_angles_sequence):
        # 偏光板を回転
        polarizer.degree = degrees(radians_light)

        print(f"  {i+1}/{len(light_angles_sequence)}: {polarizer.degree}")

        # 少し待ってから撮影
        cv2.waitKey(500)
        ret, frame = cap.readHDR(t_min, t_max, num=num, t_ref=t_ref)
        
        # 偏光画像のデモザイキング
        img_demosaiced = pa.demosaicing(frame)

        for img, radians_camera in zip( cv2.split(img_demosaiced), camera_angles_sequence):
            # OpenEXR画像の書き出し
            name = f"{dir_name}/{dir_name}_l{int(degrees(radians_light))}_c{int(degrees(radians_camera))}.exr"
            cv2.imwrite(name, img.astype(np.float32))
            # JPEG画像の書き出し
            os.makedirs(f"{dir_name}/JPG", exist_ok=True)
            name = f"{dir_name}/JPG/{dir_name}_l{int(degrees(radians_light))}_c{int(degrees(radians_camera))}.jpg"
            cv2.imwrite(name, (img*255).astype(np.uint8))
        
        # 撮影したの画像と角度情報をリストに追加
        imlist += cv2.split(img_demosaiced)
        anglist_light  += [radians_light]*4
        anglist_camera += camera_angles_sequence
    
    cap.release()
    
    # リストをndarray形式に変換
    images = cv2.merge(imlist)
    angles_light  = np.array(anglist_light)
    angles_camera = np.array(anglist_camera)

    # ミュラー行列を求める
    print("Calculate the Mueller matrix")
    img_mueller = pa.calcMueller(images, angles_light, angles_camera)
    img_m11, img_m12, img_m13,\
    img_m21, img_m22, img_m23,\
    img_m31, img_m32, img_m33  = cv2.split(img_mueller)

    np.save(f"{dir_name}/{dir_name}_img_mueller.npy", img_mueller)
    
    # 求めたミュラー行列をプロットして保存
    print("Plot the Mueller matrix")
    pa.plotMueller(f"{dir_name}/{dir_name}_plot_mueller.png", img_mueller, vabsmax=0.5)

if __name__=="__main__":
    main()
