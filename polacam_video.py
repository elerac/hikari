import cv2
import numpy as np
import polanalyser as pa
import EasyPySpin

def main():
    cap = EasyPySpin.VideoCapture(0)
    cap.set(cv2.CAP_PROP_GAMMA, 1.0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 30000)
    cap.set(cv2.CAP_PROP_GAIN, 0)
    
    scale = 0.25

    while True:
        ret, frame = cap.read()
        
        img_demosaiced = pa.demosaicing(frame, pa.COLOR_PolarMono)
        
        img_demosaiced = cv2.resize(img_demosaiced, None, fx=scale, fy=scale)

        angles = np.deg2rad([0, 45, 90, 135])
        img_stokes = pa.calcStokes(img_demosaiced, angles)

        img_intensity = pa.cvtStokesToIntensity(img_stokes)
        img_DoLP      = pa.cvtStokesToDoLP(img_stokes)
        img_AoLP      = pa.cvtStokesToAoLP(img_stokes)

        img_intensity_u8 = np.clip( 255.0*((img_intensity/255.0)**(1/2.2)), 0, 255).astype(np.uint8)
        img_DoLP_u8 = np.clip(255.0*img_DoLP, 0, 255).astype(np.uint8)
        img_AoLP_u8 = pa.applyColorToAoLP(img_AoLP, img_DoLP)

        cv2.imshow("intensity", img_intensity_u8)
        cv2.imshow("DoLP", img_DoLP_u8)
        cv2.imshow("AoLP", img_AoLP_u8)

        key = cv2.waitKey(30)
        if key == ord("q"):
            break

if __name__ == "__main__":
    main()

