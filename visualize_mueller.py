import numpy as np
import polanalyser as pa

def main():
    img_mueller = np.load("img_mueller.npy")

    pa.plotMueller("img_mueller.png", img_mueller, vabsmax=0.5, dpi=400)

if __name__=="__main__":
    main()
