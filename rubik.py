import numpy as np
import pyautogui as pg
import kociemba as kb
import time

##### 初始化 - 获取魔方位置信息 #####
def cube_initialize(standard: bool = True):
    """获取魔方位置信息"""
    if standard: # 标准情形：图像置于左侧
        center, l1 = np.array([535, 662]), 246
    else: # 否则要求输入两个特定位置
        input("按回车录入中心点位置")
        center = np.array(pg.position())
        input("按回车录入底部位置")
        bottom = np.array(pg.position())
        l1 = bottom[1] - center[1]
        print("中心位置",center, "垂直长度", l1)
    l2, l3 = l1 * 208 // 246, l1 * 122 // 246
    left, right, down = [np.array(p) //3 for p in [[-l2, -l3], [l2, -l3], [0, l1]]]
    return center, left, right, down

# numpy 数组转化为元组
array_to_tuple = lambda arr:tuple(int(i) for i in arr)
# 小面集转化为元组
facets_to_tuple = lambda facets:[array_to_tuple(i) for line in facets for i in line]

def get_facets(center, left, right, down):
    """返回左，右，上，三面的小面位置"""
    left_origin, right_origin, up_origin = [center + i // 2 for i in [left + down, right + down, left + right]]
    lefts = [[left_origin + (2 - i) * left + j * down for i in range(3)] for j in range(3)]
    rights = [[right_origin + i * right + j * down for i in range(3)] for j in range(3)]
    ups = [[up_origin + i * right + (2 - j) * left for i in range(3)]for j in range(3)]
    return [facets_to_tuple(facets) for facets in [lefts, rights, ups]]

def check_positions(facets):
    for p in facets:
        time.sleep(0.2)
        pg.moveTo(p)
    return 


###### 图像识别 - 获取魔方位置分布 #######
colors = {'white': ((252, 244, 252), (222, 215, 222), (198, 192, 198)),
 'red': ((236, 56, 35), (208, 50, 30), (186, 44, 27)),
 'blue': ((64, 168, 198), (56, 148, 174), (51, 132, 155)),
 'green': ((128, 200, 55), (113, 176, 49), (101, 157, 44)),
 'orange': ((252, 138, 10), (222, 122, 9), (198, 109, 8)),
 'yellow': ((252, 237, 71), (222, 208, 63), (198, 186, 56))}

diff = lambda c1, c2: sum(abs(i - j) for i, j in zip(c1, c2))

def find_color(img, pos, side = 0):
    """
    匹配三维数组 color 对应的颜色
    side 参数如下：
       - 0 小面位于上方
       - 1 小面位于左侧
       - 2 小面位于右侧
    """
    color = img.getpixel(pos)
    return min(colors.keys(), key = lambda c: diff(colors[c][side], color))

color_to_facet = {"white":"U", "red":"L", "blue":"F", "green":"B", "orange":"R", "yellow":"D"}
facet_to_color = {val:key for key, val in color_to_facet.items()}

def color_distribution(im, ups, lefts, rights, shift = False):
    """获取颜色分布，第二位置时修改"""
    face_U = [color_to_facet[find_color(im, p)] for p in ups]
    face_L = [color_to_facet[find_color(im, p, 1)] for p in lefts]
    face_F = [color_to_facet[find_color(im, p, 2)] for p in rights]
    if not shift: # 初始界面
        return face_U, face_L, face_F
    # 扭转后的界面
    face_B, face_R, face_D = face_U, [face_L[i-1] for i in (7,4,1,8,5,2,9,6,3)], face_F[::-1]
    return face_B, face_R, face_D

##### 获取魔方分布信息 #####
def shift_faces(center, down):
    """左滑和上移"""
    d = int(down[1])
    corner = array_to_tuple(center + (3 * d, 3 * d))
    pg.moveTo(corner, duration=0.1)
    pg.dragRel(-d, 0, duration=0.25)
    pg.moveTo(corner, duration=0.1)
    pg.dragRel(-d, 0, duration=0.25)
    pg.moveTo(corner, duration=0.1)
    pg.dragRel(0, -d, duration=0.25)
    return

