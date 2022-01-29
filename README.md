## 基于图像识别的魔方自动还原

在 B 站看了一个用 Python 自动复原魔方的[视频](https://www.bilibili.com/video/BV12i4y1G74V)，觉得还蛮有意思，就自己动手写了个工具，附代码[地址](https://github.com/RexWzh/rubik_cube.py)。废话不多说，先看演示吧。

1. 随机打乱一个魔方（图片）
   <img src="http://qiniu.wzhecnu.xyz/cube/initial.gif" width= "80%">

2. 导入工具，一行代码还原魔方
   ```py
   from rubik import *
   Cube().auto_solve_cube(wait=False)
   ```
   <img src="http://qiniu.wzhecnu.xyz/cube/solve.gif" width= "80%">

---

## 工具原理
工具依赖两个 Python 包，以及浏览器插件：
   - pyautogui: 用于识别图像和执行操作
   - kociemba: 用于求解魔方
   - Rubik's Cube：浏览器插件

### 整体思路
分几步进行：
   1. 计算魔方的小面位置
   2. 识别魔方状态
   3. 根据魔方状态计算公式
   4. 将公式实现为电脑操作

### 具体细节
1. 获取小面位置
   - 获取一点位置 + 一边长度，则整个魔方的位置确定
      <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128172937.png" width = "50%">
   - 计算三个基本向量，进而得到 27 个小面的位置
      <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128174645.png" width = "50%">

2. 魔方状态码
    - 魔方状态码是 `URFDLB` 构成的字符串，`URFDLB` 是魔方六个面的缩写，其中 U 为顶面（up），R 为右面（right），F 为正面（Front），D 为顶面（down），L 为左面（Left），B 为背面（Back）
    - 状态码按如下展开图的标号顺序读入
      ```python
                  |************|
                  |*U1**U2**U3*|
                  |************|
                  |*U4**U5**U6*|
                  |************|
                  |*U7**U8**U9*|
                  |************|
      ************|************|************|************
      *L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*
      ************|************|************|************
      *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*
      ************|************|************|************
      *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*
      ************|************|************|************
                  |************|
                  |*D1**D2**D3*|
                  |************|
                  |*D4**D5**D6*|
                  |************|
                  |*D7**D8**D9*|
                  |************|
      ```
   - 比如还原状态为 `UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB`

3. 识别魔方状态：
   - 将正视图“上，左，右”的三面视为 `U, L, F`，截图获取分布信息
      <img src="">
   - 滑动到背面，获取后三面的分布信息
      <img src=".gif">
   - 两部分信息整合，导出状态码

4. 获取魔方公式
   - 魔方公式为 `U, U', U2, R, R', R2...` 等构成的列表
   - `U, U', U2` 分别代表顶面顺时针旋转 90°，逆时针旋转 90°，以及旋转旋转 180°，其他各面规则同理
   - 调用 `kociemba.solve` 获取公式
   
5. 将公式实现为操作
   - 转动的位置参数由“小面位置”和“基本向量”得到
   - 用 pyautogui 的函数 `moveTo` 和 `dragRel` 实现鼠标移动和拖拽

由于函数间需频繁共享位置数据，因而使用面向对象编程。（如果换成 Julia，面向对象可用多重派发代替，将数据部分写为结构体）

## 使用介绍
### 安装依赖
仅介绍 Ubuntu 系统安装依赖的方法，其他系统类似。
1. 安装 Python 包
   ```bash
   pip install pyautogui # 安装自动化工具
   pip install kociemba # 安装魔方工具
   ```

2. Ubuntu 下，使用 `pyautogui` 的截图工具需安装依赖 scrot
   ```bash
   sudo apt-get install scrot
   ```

3. 在 Chrome 浏览器的应用商场，搜索 `rubik` 并安装插件
    ![深度截图_选择区域_20220128171120](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/深度截图_选择区域_20220128171120.png)

### 基本使用

1. 初始化类对象
   ```py
   cube = Cude(standard=False)
   ```

2. 检查 27 个小面位置
   ```py
   cube.check_facets()
   ```

3. 检查魔方的基本旋转
   ```py
   cube.check_basic_moves() # 检查基本旋转是否正确
   ```

4. 获取魔方分布信息，并打印魔方展开图
   ```py
   state = cube.get_cube_distribution() # 获取小面分布信息
   print(expand_cube(state))
   ```

5. 自动识别并求解魔方
   ```py
   cube.auto_solve_cube()
   ```

6. 根据魔方代码，构造给定的魔方状态
   ```py
   state = "UBRLUFFUBLRUFRLLLRDBDRFDBBUDDBUDDLRFBFLDLBFFRFLRUBRDUU"
   cube.to_state(state)
   ```

### 文件说明
1. `src` 目录下有三个文件：
   - `rubik.py`：主文件，定义类对象 `Cube`
   - `data.py`：存储魔方的色块颜色等信息
   - `tools.py`：基本函数工具
   
2. `demo` 目录下
   - `demo.py` 给出演示例子
   - `quick_start.py` 工具快捷调用

---

## 写在最后
这是随手写的实战项目，在编写模块方面，个人还欠缺规范性；比如没有添加 CI/CD，帮助文档，文件系统也没有添加 Python 包常见的 `__init__.py` 等。这些将在后续进一步学习后，再改进和提升。