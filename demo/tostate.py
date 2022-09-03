#!/bin/env python3
# author: zhwang
# date: 2022-04-19
# description: 打开魔方插件，并双击进入待准备状态；在项目目录下，运行 `python src/tostate.py` 将魔方化为指定状态。
import sys
sys.path.append("./src/")
sys.path.append("../src/")
import time

from tools import expand_cube
import kociemba as kb
from rubik import Cube

txt = "DUDUUUDUDBRBRRRBRBLFLFFFLFLUDUDDDUDUFLFLLLFLFRBRBBBRBR"
state = input(f"请输入魔方状态的代码，直接回车使用示例代码\n示例：\n{txt}\n")

if not state: state = txt
try:
    kb.solve(state) # 检验是否有效
except:
    print("魔方代码输入有误！请检查")
    print(expand_cube(state))
print("输入魔方的展开图如下")
print(expand_cube(state))

cube = Cube()

input("按回车，开始构造给定魔方：")
sol = cube.to_cube_state(state)
print("魔方解法为")
for i in sol:
    print(i,end="\t")

time.sleep(.2)
cube.get_cube_distribution();