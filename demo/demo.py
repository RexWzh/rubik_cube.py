#!/usr/bin/python3
# author: zhwang
# date: 2022-01-30
# description: 打开魔方插件，并双击进入待准备状态；在项目目录下，运行 `python src/demo.py` 进行魔方还原。

import sys
sys.path.append("./src/")
from rubik import *

### 示例一
print("######### 示例 1 开始 #############")
print("将页面放在左侧，充满半边，使用默认参数")
input("将魔方打乱，按回车开始：")
cube = Cube()

s = input("是否检验魔方的小面位置，回车确认检查，否则输入 0：")
if s != "0":
    cube.check_facets()

input("按回车，开始自动观察并还原魔方：")
cube.auto_solve_cube(wait=False)

print("######### 示例 1 结束 #############")


### 示例二，手动输入位置
print("######### 示例 2 开始 #############")
print("将魔方打乱，按提示，将鼠标移动到相应位置")
cube = Cube(standard=False)

s = input("是否检验魔方的小面位置，回车确认检查，否则输入 0：")
if s != "0":
    cube.check_facets()

input("按回车，开始自动观察并还原魔方：")
cube.auto_solve_cube(wait=False)
print("######### 示例 2 结束 #############")


### 示例三，输入给定状态
print("######### 示例 3 开始 #############")
txt = "UBRLUFFUBLRUFRLLLRDBDRFDBBUDDBUDDLRFBFLDLBFFRFLRUBRDUU"
state = input("请输入魔方状态的代码，按回车使用示例代码\n示例：\n%s\n"%txt)
if not state: state = txt
try:
    kb.solve(state) # 检验是否有效
except:
    print("魔方代码输入有误！请检查")
    print(expand_cube(state))
print("输入魔方的展开图如下")
print(expand_cube(state))


standard = input("是否使用默认位置，默认是，否则输入 0:")
standard = True if standard != "0" else False
cube = Cube(standard=standard)

s = input("是否检验魔方的小面位置，回车确认检查，否则输入 0：")
if s != "0":
    cube.check_facets()


input("按回车，开始构造给定魔方：")
sol = cube.to_cube_state(state)
print("魔方解法为")
for i in sol:
    print(i,end="\t")

print("\n######### 示例 3 结束 #############")