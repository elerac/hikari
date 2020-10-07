"""
Geometric calibration
"""
import numpy as np

def cvtHeterogeneousToHomogeneous(points_hetero: np.ndarray) -> np.ndarray:
    """
    Convert Heterogeneous coordinates to Homogeneous coordinates system

    Parameters
    ----------
    points_hetero : np.ndarray, (N, 3) or (N, 2)
        Points in the Heterogeneous coordinate system
    Returns
    -------
    points_homoge : np.ndarray, (N, 4) or (N, 3)
        Points in the Homogeneous coordinate system
    """
    N, dim = points_hetero.shape
    points_homoge = np.ones((N, dim+1), dtype=points_hetero.dtype)
    points_homoge[:,:-1] = points_hetero
    return points_homoge

def calibrateCamera(objpoints: np.ndarray, imgpoints: np.ndarray) -> np.ndarray:
    """
    Calibrate camera

    Parameters
    ----------
    objpoints : np.ndarray, (N, 3)
        3D world point
    imgpoints : np.ndarray, (N, 2)
        2D image point
    
    Returns
    -------
    camera_matrix : np.ndarray, (3, 4)
        camera matrix
        [[c11, c12, c13, c14],
         [c21, c22, c23, c24],
         [c32, c32, c33, c34]]
    """
    # Check input array size
    obj_N, obj_dim = objpoints.shape
    img_N, img_dim = imgpoints.shape
    assert obj_dim==3,   f"'objpoints' dimention must be 3: {obj_dim}"
    assert img_dim==2,   f"'imgpoints' dimention must be 2: {img_dim}"
    assert obj_N==img_N, f"Arrays must be the same size. objpoints:{obj_N}, img_points:{img_N}"
    
    N = obj_N

    # Build matrix
    A = np.zeros((N * 2, 11))
    b = np.zeros((N * 2))
    c34 = 1.0
    for i in range(N):
        X, Y, Z = objpoints[i]
        x, y    = imgpoints[i]

        A[2 * i]     = [X, Y, Z, 1, 0, 0, 0, 0, -X * x, -Y * x, -Z * x]
        A[2 * i + 1] = [0, 0, 0, 0, X, Y, Z, 1, -X * y, -Y * y, -Z * y]
        b[2 * i]     = c34 * x
        b[2 * i + 1] = c34 * y

    # Solve Ax=b
    A_pinv = np.linalg.pinv(A)
    x = A_pinv @ b # [c11, c12, c13, c14, c21, c22, c23, c24, c31, c32, c33]

    camera_matrix = np.append(x, c34).reshape((3, 4))
    return camera_matrix

def calibrateCamera1D(objpoints: np.ndarray, imgpoints: np.ndarray) -> np.ndarray:
    """
    Calibrate camera 1D
    1D camera matrix(2x4) is defined as the original camera matrix(3x4) with the y-axis removed

    Parameters
    ----------
    objpoints : np.ndarray, (N, 3)
        3D world point
    imgpoints : np.ndarray, (N,)
        1D image point
    
    Returns
    -------
    camera_matrix_1d : np.ndarray, (2, 4)
        camera matrix 1D
        [[c11, c12, c13, c14],
         [c32, c32, c33, c34]]
    """
    # Check input array size
    obj_N, obj_dim = objpoints.shape
    img_N = imgpoints.shape[0]
    assert obj_dim==3,   f"'objpoints' dimention must be 3: {obj_dim}"
    assert obj_N==img_N, f"Arrays must be the same size. objpoints:{obj_N}, img_points:{img_N}"
    
    N = obj_N

    # Build matrix
    A = np.zeros((N, 7))
    b = np.zeros((N))
    c34 = 1.0
    for i in range(N):
        X, Y, Z = objpoints[i]
        x       = imgpoints[i]

        A[i] = [X, Y, Z, 1, -X * x, -Y * x, -Z * x]
        b[i] = c34 * x

    # Solve Ax=b
    A_pinv = np.linalg.pinv(A)
    x = A_pinv @ b # [c11, c12, c13, c14, c31, c32, c33]

    camera_matrix_1d = np.append(x, c34).reshape((2, 4))
    return camera_matrix_1d

def main():
    import cv2
    N = 20

    # 実世界の3次元座標
    objpoints = np.random.rand(N, 3) # (N, 3)
    
    # 適当なカメラ行列を作る
    #camera_matrix = np.random.rand(3, 4) # (3, 4)
    #camera_matrix[-1, -1] = 1 # set c34=1
    f = 100
    c = [300, 200]
    K = np.array([[f, 0, 300],
                  [0, f, 200],
                  [0, 0, 1]])
    R = np.random.rand(3, 3)
    t = np.random.rand(3) * 10
    Rt = np.vstack([R.T, t]).T
    camera_matrix = K @ Rt
    print("Camera matrix GT:\n", camera_matrix)
    
    # カメラに3次元点を投影
    X = cvtHeterogeneousToHomogeneous(objpoints)
    noise = np.random.normal(0, 0.5, (N, 3)) * 0.001
    noise = 0
    x = (camera_matrix @ X.T).T + noise
    
    # 点が画像中に投影された2次元座標
    img_points = x[:,:2] / np.expand_dims(x[:,2], 1) # (N, 2)
    
    # 対応した点からキャリブレーション
    camera_matrix = calibrateCamera(objpoints, img_points)
    print("Camera matrix estimate:\n", camera_matrix)
    
    camera_matrix_1d = calibrateCamera1D(objpoints, img_points[:,0])
    print("Camera matrix 1D estimate:\n", camera_matrix_1d)
    
    # 結果を保存
    fs = cv2.FileStorage('calibration_result.xml', cv2.FILE_STORAGE_WRITE)
    fs.write('camera_matrix', camera_matrix)
    fs.release()
    
if __name__=="__main__":
    main()
