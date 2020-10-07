"""
3D reconstruction and write points
"""
import numpy as np
import os

def write_ply(filename: str, points_3D: np.ndarray):
    """
    Export 3D points to ply file

    Parameters
    ----------
    filename : str
        ply file name
    points_3D : np.ndarray, (N, 3)
        3D points
    """
    name, ext = os.path.splitext(filename)
    assert ext==".ply", f"'filename' extension must be '.ply': '{filename}'"

    N = len(points_3D)
    header  = 'ply\n'
    header += 'format ascii 1.0\n'
    header += f'element vertex {N}\n'
    header += 'property double x\n'
    header += 'property double y\n'
    header += 'property double z\n'
    #header += 'property uchar red\n'
    #header += 'property uchar green\n'
    #header += 'property uchar blue\n'
    header += 'end_header\n'
    with open(filename, 'w') as f:
        f.write(header)
        for x, y, z in points_3D:
            f.write(f'{x} {y} {z}\n')
            #b, g, r = (0, 0, 0)
            #f.write('{} {} {} {} {} {}\n'.format(x, y, z, r, g, b))

def write_obj(filename: str, points_3D: np.ndarray) -> None:
    """
    Export 3D points to obj file

    Parameters
    ----------
    filename : str
        obj file name
    points_3D : np.ndarray, (N, 3)
        3D points
    """
    name, ext = os.path.splitext(filename)
    assert ext==".obj", f"'filename' extension must be '.obj': '{filename}'"

    with open(filename, 'w') as f:
        for x, y, z in points_3D:
            f.write(f'v {x} {y} {z}\n')

def triangulatePoints(camera_matrix1: np.ndarray,
                      camera_matrix2: np.ndarray, 
                      imgpoints1: np.ndarray, 
                      imgpoints2: np.ndarray) -> np.ndarray:
    """
    Reconstruction 3D

    Parameters
    ----------
    camera_matrix1 : np.ndarray, (3, 4)
        camera matrix 1
    camera_matrix2 : np.ndarray, (2, 4)
        1D camera matrix
    imgpoints1 : np.ndarray, (N, 2)
        2D image points
    imgpoints2 : np.ndarray, (N,)
        1D image points
    Returns
    -------
    points_3D : np.ndarray, (N, 3)
        reconstructed 3D points
    """
    c11, c12, c13, c14, c21, c22, c23, c24, c31, c32, c33, c34 = camera_matrix1.flatten()
    p11, p12, p13, p14, p21, p22, p23, p24 = camera_matrix2.flatten()
    
    # Check array size
    N1, dim = imgpoints1.shape
    N2 = imgpoints2.shape[0]
    assert N1==N2, f"'imgpoints1' and 'imgpoints2' length must be same size: {N1}!={N2}"

    N = N1
    
    # Reconstruction per points
    points_3D = np.empty((N, 3))
    for i, (point1, point2) in enumerate(zip(imgpoints1, imgpoints2)):
        x1, y1 = point1
        x2 = point2
        
        F = np.array( [c34*x1-c14, c34*y1-c24, p24*x2-p14]) # (3,)
        Q = np.array([[c11-c31*x1, c12-c32*x1, c13-c33*x1],
                      [c21-c32*y1, c22-c32*y1, c23-c33*y1],
                      [p11-p21*x2, p12-p22*x2, p13-p23*x2]]) # (3, 3)
        V = np.linalg.solve(Q, F) # (3,)
        
        points_3D[i] = V

    return points_3D


def main():
    # 3次元計測の例
    projMatr1 = np.random.rand(3, 4)
    projMatr2 = np.random.rand(2, 4)
    projPoints1 = np.random.rand(50, 2)
    projPoints2 = np.random.rand(50)

    points_3D = triangulatePoints(projMatr1, projMatr2, projPoints1, projPoints2)

    write_obj("points3D.obj", points_3D)


    # 3次元データ書き出しの例
    #（球の点群を書き出し）
    N = 5000
    r = 1
    theta = np.random.rand(N) * np.pi
    phi = np.random.rand(N) * np.pi*2
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    points_3D = np.array([x, y, z]).T
    write_obj("sphere.obj", points_3D)
    write_ply("sphere.ply", points_3D)

if __name__=="__main__":
    main()
