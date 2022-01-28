import numpy as np
import pyautogui as pg
from data import *

"""
魔方图像操作和运算的函数工具
"""

array_to_tuple = lambda arr: tuple(int(i) for i in arr)
array_to_tuple.__doc__ = """将 <numpy 数组> 转化为 <整型元组>

Args:
    arr (numpy.ndarray): numpy 数组

    Returns:
       tuple(int): 整型元组
       
说明：
   - 此函数用于转化数据格式
   - 一些输入不能支持 numpy 的数组类型
   - 整数输入不能支持 `numpy.int64` 类型
"""

facets_to_tuple = lambda facets:[array_to_tuple(i) for line in facets for i in line]
facets_to_tuple.__doc__ = """二维列表展平，并将数据类型从 <numpy 数组> 化为 <整型元组>

Args:
    facets (list(list(numpy.ndarray))): numpy 数组构成的二维列表

    Returns:
       list(tuple(int)): 整型元组构成的一维列表列表
"""

diff = lambda c1, c2: sum(abs(i - j) for i, j in zip(c1, c2))
diff.__doc__ = """计算位置差的绝对值之和

Args:
    c1 (tuple(int)): 整数元组，表示颜色信息，长度为 3
    c1 (tuple(int)): 整数元组，表示颜色信息，长度为 3

    Returns:
       int: 位置差的绝对值之和
"""

def cube_initialize(standard: bool = True):
    """获取魔方位置信息

    Args:
        standard (bool, optional): [description]. Defaults to True.

    Returns:
        center (numpy.ndarray): 中心点位置
        left (numpy.ndarray): 左上方向的单位向量（长度为魔方小面的边长）
        right (numpy.ndarray): 右上方向的单位向量
        down (numpy.ndarray): 往下方向的的单位向量
    
    补充说明：
       1. 参数 `standard` 设置是否使用标准位置
           - 标准情形将魔方窗口至于左侧，且自动铺满半边
           - 不同电脑标准位置可能不同
           - 使用标准位置，方便代码调试，初始化类时，不需要额外输入信息
       2. 返回数据类型均为 numpy，为方便坐标运算
       3. 图像初始化有两个重要信息：
           - 魔方中心位置
           - 魔方的尺寸
       4. 魔方位置和尺寸通过 pyautogui.position() 获取
       5. 图像的一点和一边确定，整个图像就确定了；但更实用的考虑，可以用 OpenCV 的 `matchTemplate` 和 `minMaxLoc` 匹配图像，而不必另外输入。
    """
    if standard:
        center, l1 = np.array([535, 669]), 290
    else:
        input("按回车录入中心点位置")
        center = np.array(pg.position())
        input("按回车录入底部位置")
        bottom = np.array(pg.position())
        l1 = bottom[1] - center[1]
        print("中心位置",center, "垂直长度", l1)
    l2, l3 = l1 * 208 // 246, l1 * 122 // 246
    left, right, down = [np.array(p) //3 for p in [[-l2, -l3], [l2, -l3], [0, l1]]]
    return center, left, right, down


def check_positions(positions) -> None:
    """将鼠标依次移动到指定位置

    Args:
        positions (list(tuple(int))): 由若干二元元组构成的列表，记录位置信息
    
    Return:
        None: 不返回值
    
    补充说明：
       - 移动的时间间隔为 0.2s
       - 函数用于检验获取位置的正确性
    """
    for p in positions:
        time.sleep(0.2)
        pg.moveTo(p)
    return


def find_color(img, pos, side = 0) -> str:
    """返回指定位置像素点匹配的颜色

    Args:
        img (PIL.PngImagePlugin.PngImageFile): `pyautogui.screenshot()` 的截图图像
        pos (tuple(int, int)): 像素位置
        side (int, optional): 像素所在位置. Defaults to 0.

    Returns:
        str: 匹配到的颜色，比如 white
    
    补充说明：
       1. side 参数如下：
          - 0 小面位于上方
          - 1 小面位于左侧
          - 2 小面位于右侧
       2. Google 插件的魔方图像中，同色块在三个方向的像素有较大区别，所以匹配所在面的颜色信息，增加准确性。
    """
    color = img.getpixel(pos)
    return min(colors.keys(), key = lambda c: diff(colors[c][side], color))


def reverse_operation(op: str) -> str:
    """将魔方操作转为逆操作
    
    Args:
        op (str): 魔方操作的字符

    Returns:
        str: 逆操作的字符
    """
    if len(op) == 1:
        return op + "'"
    if op[-1] == "'":
        return op[0]
    return op


reverse_operations = lambda solution:[reverse_operation(op) for op in solution[::-1]]
reverse_operations.__doc__ = """将魔方系列操作转为逆操作

Args:
    solution (list(str)): 魔方操作列表

    Returns:
        list(str)： 给定操作的逆操作列表

说明：
   - 用于生成给定的魔方
   - 还原状态 + 逆操作 = 给定状态
"""