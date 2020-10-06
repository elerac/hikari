import matplotlib.pyplot as plt
import numpy as np

def plotStokesArrow(filename: str, stokes_vector: np.ndarray,
                    arrow_num : int=4, arrow_color: str='dodgerblue', arrowstyle: str='<|-|>',
                    draw_ellipse : bool=True, ellipse_color: str='black',
                    dpi: int=100) -> None: 
    """
    ストークスベクトルを入力すると，偏光状態を矢印で描画します

    Parameters
    ----------
    filename : str
        出力するファイル名
    stokes_vector : np.ndarray
        ストーククスベクトル (3,)
    arrow_num : int
        矢印の数
    arrow_color : str
        矢印の色
    arrowstyle : str
        矢印の形
        '-'にすると，普通の線になる
        詳しくは，https://matplotlib.org/3.3.1/api/_as_gen/matplotlib.patches.ArrowStyle.html
    draw_ellipse : bool
        矢印を囲む楕円を描画するかどうか
    ellipse_color : str
        矢印を囲む色
    dpi : int
        出力するサイズ
    """

    S = stokes_vector
    S = S/S[0] # 正規化
    DoLP = np.sqrt(S[1]**2+S[2]**2)/S[0] # 0~1
    AoLP = np.mod(0.5*np.arctan2(S[2], S[1]), np.pi) # 0~np.pi
    
    # 回転行列を定義
    R = lambda theta: np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    
    # 矢印を描画
    for theta in np.linspace(0, np.pi/2, num=arrow_num+1):
        # 始点
        x1 = np.cos(2*theta)
        y1 = (1-DoLP)*np.sin(2*theta)
        
        # 終点
        x2 = np.cos(2*theta+np.pi)
        y2 = (1-DoLP)*np.sin(2*theta+np.pi)
        
        # 点を回転
        x, y = R(AoLP) @ np.array([[x1, y1], [x2, y2]]).T
        
        # 描画
        arrowprops = dict(arrowstyle=arrowstyle, linewidth=2, color=arrow_color)
        plt.annotate('', (x[0], y[0]), (x[1], y[1]), arrowprops=arrowprops)

    # 矢印を囲む楕円を描画
    if draw_ellipse:
        theta_sequence = np.linspace(0, np.pi, num=200)
        x = np.cos(2*theta_sequence)
        y = (1-DoLP)*np.sin(2*theta_sequence)
        p = R(AoLP) @ np.array([x, y])
        plt.plot(p[0], p[1], c=ellipse_color, lw=0.5)
    
    # グラフの設定
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlim(-1, 1)
    plt.ylim(-1, 1)
    plt.axis('off')
    
    # 描画結果を出力
    plt.savefig(filename, bbox_inches='tight', dpi=dpi)

    plt.close('all')


def main():
    S = np.array([1, 0, 0])
    print(f"Stokes: {S}")
    plotStokesArrow("stokes_arrow-1.png", S)
    
    S = np.array([1, 0.6, 0.2])
    print(f"Stokes: {S}")
    plotStokesArrow("stokes_arrow-2.png", S)
    
    S = np.array([1, 0, 1])
    print(f"Stokes: {S}")
    plotStokesArrow("stokes_arrow-3.png", S)

if __name__=='__main__':
    main()
