#!/usr/bin/python3
# author: zhwang
# date: 2022-04-19
# description: 打开魔方插件，并双击进入待准备状态；在项目目录下，运行 `python src/quick_start.py` 进行魔方还原。
import sys
sys.path.append("..")
from rubik import *

while True:
    input("先双击屏幕，魔方打乱后按回车开始：")
    cube = Cube(interval=0.13)
    cube.check_facets(sides=[0])
    start = input("如果无误，按回车继续，否则输入 0 重新识别：")
    if start != "0":
        while True:
            cube.auto_solve_cube(wait=False)
            isend = input("执行结束，按回车处理下一个，输入其他结束：")
            if len(isend):
                break
    else:
        continue
    break