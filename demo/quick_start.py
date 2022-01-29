import sys
sys.path.append("./src/")
from rubik import *

print("先双击屏幕，将魔方打乱再进行下一步")
s = input("默认使用固定位置，输入 0 重新定位魔方位置：")
standard = False if s == "0" else True
cube = Cube(standard=standard, interval=0.3)
cube.check_facets((0,))
cube.auto_solve_cube(wait=False)