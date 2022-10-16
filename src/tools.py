import numpy as np
import pyautogui as pg
import time, cv2
from PIL import Image
from data import colors,init_txt

"""
图像操作和运算的函数工具
"""

def cv2PIL(img_cv):
    """
    
    """
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

def PIL2cv(img_pil):
    """PIL 图像转 opencv 图像

    Args:
        img_pil (PILImage): 输入图像

    Returns:
        numpy.ndarray: 输出图像
    """
    return cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGB2BGR)

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

def expand_cube(state: str = "") -> str:
    """返回魔方状态的展开图

    Args:
        state (str, optional): 魔方状态. 默认空字符代表初始状态.

    Returns:
        str: 展开的魔方图
        
    还原状态：
       - UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB
    """
    if not state: # 返回初始状态
        state = init_txt
    res = init_txt
    for i,face in enumerate("URFDLB"):
        for j in range(9):
            res = res.replace(face + str(j+1), state[9 * i + j])
    return res