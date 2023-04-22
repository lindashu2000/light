
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import make_interp_spline
import scipy


def draw_line(title, x=list(), y=list()):
    # 准备绘制数据
    # "r" 表示红色，marksize用来设置'D'菱形的大小
    plt.plot(x, y, "r.-", label='origin')

    # xs = np.linspace(min(x), max(x), 20)
    # ys = make_interp_spline(x, y)(xs)
    # plt.plot(xs, ys, "g.-", label='spline')

    # y_smooth = scipy.signal.savgol_filter(y, len(x), 3)
    # 亦或
    y_smooth2 = scipy.signal.savgol_filter(y, 3, 1, mode='nearest')
    plt.plot(x, y_smooth2, "b.-", label='savgol')

    # 绘制坐标轴标签
    plt.xlabel("strike price")
    plt.ylabel("bid price")
    plt.title(title)
    # 显示图例
    plt.legend(loc="upper right")
    # 调用 text()在图像上绘制注释文本
    # x1、y1表示文本所处坐标位置，ha参数控制水平对齐方式, va控制垂直对齐方式，str(y1)表示要绘制的文本
    for x1, y1 in zip(x, y):
        plt.text(x1, y1, str(y1), ha='center', va='bottom', fontsize=10)
    # 保存图片
    # plt.savefig(title+".jpg")
    plt.show()
