import numpy as np
import pyautogui as pg
import time, cv2
from PIL import Image
from rubik.data import color_table, inds_txt, init_state, compact_inds_txt, face_inds_txt

screenshot = lambda : pg.screenshot().resize(pg.size())
screenshot.__doc__ = """屏幕截图

## 特别留意

pyautogui 截图的像素坐标和实际操作的坐标存在差异，这里使用 resize 调整

Ref: https://stackoverflow.com/questions/45302681/running-pyautogui-on-a-different-computer-with-different-resolution
"""

def cv2PIL(img_cv):
    """opencv 图像转 PIL 图像

    Args:
        img_cv (numpy.ndarray): 输入图像
    
    Returns:
        PILImage: 输出图像
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

def expand_cube(state: str = "", compact=True) -> str:
    """返回魔方状态的展开图

    Args:
        state (str, optional): 魔方状态. 默认空字符代表初始状态.

    Returns:
        str: 展开的魔方图
        
    还原状态：
       - UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB
    """
    
    if not state: # 返回初始状态
        state = init_state
    res = inds_txt if not compact else compact_inds_txt
    for i, face in enumerate("URFDLB"):
        for j in range(9):
            res = res.replace(face + str(j+1), state[9 * i + j])
    return res

def expand_face(state):
    """魔方一面的展开图"""
    assert len(state) == 9, f"单面数目错误！请检查{len(state)}"
    return face_inds_txt.format(*state)

def face_rotate(state, deg):
    """魔方面顺时针旋转 90°"""
    deg %= 4
    if deg == 0: return state
    order = (6, 3, 0, 7, 4, 1, 8, 5, 2)
    if isinstance(state, str): # 对 state 类型进行派发
        state = ''.join(state[i] for i in order)
    elif isinstance(state, list):
        state = [state[i] for i in order]
    return face_rotate(state, deg - 1)
