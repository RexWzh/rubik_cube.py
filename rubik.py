import numpy as np
import pyautogui as pg
import kociemba as kb
import time


def cube_initialize(standard: bool = True):
    if standard: # 标准情形：图像置于左侧
        center = np.array([535, 662])
        l1 = 246
    else: # 否则要求输入两个特定位置
        input("按回车录入中心点位置")
        center = np.array(pg.position())
        input("按回车录入底部位置")
        bottom = np.array(pg.position())
        l1 = bottom[1] - center[1]
    l2, l3 = l1 * 208 // 246, l1 * 122 // 246
    left, right, down = [np.array(p) //3 for p in [[-l2, -l3], [l2, -l3], [0, l1]]]
    return center, left, right, down

def get_facets(center, left, right, down):
    red_origin, blue_origin, white_origin = [center + i // 2 for i in [left + down, right + down, left + right]]
    reds = [[red_origin + (2 - i) * left + j * down for i in range(3)] for j in range(3)]
    blues = [[blue_origin + i * right + j * down for i in range(3)] for j in range(3)]
    whites = [[white_origin + (2 - i) * left + j * right for i in range(3)]for j in range(3)]
    return reds, blues, whites

def check_positions(facets):
    for line in facets:
        for p in line:
            time.sleep(0.2)
            pg.moveTo(list(p))