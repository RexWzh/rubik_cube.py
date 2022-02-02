import sys
sys.path.append("./src/")
sys.path.append("../src/")
from rubik import *

while True:
    print("先双击屏幕，将魔方打乱再进行下一步")
    s = input("默认使用固定位置，输入 0 重新定位魔方位置：")
    standard = False if s == "0" else True
    cube = Cube(standard=standard, interval=0.13)
    cube.check_facets()
    start = input("如果检查无误，按回车开始还原，否则输入 0 取消：")
    if start != "0":
        while True:
            cube.auto_solve_cube(wait=False)
            end = input("执行结束，按回车处理下一个，输入 0 结束：")
            if end == "0":
                break
    else:
        continue
    break