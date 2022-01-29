## 基于图像识别的魔方自动还原

在 B 站看到一个用 Python 复原魔方的[视频](https://www.bilibili.com/video/BV12i4y1G74V)，觉得还蛮有意思，就自己动手写了个工具，附代码[地址](https://github.com/RexWzh/rubik_cube.py)。废话不多说，先看演示吧。

1. 随机打乱一个魔方
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/start.gif" width= "100%">

2. 导入工具，一行代码还原魔方
   ```py
   from rubik import *
   Cube().auto_solve_cube(wait=False)
   ```
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/end.gif" width= "100%">

---

## 工具原理
工具依赖两个 Python 包，以及浏览器插件：
   - pyautogui: 用于识别图像和执行操作
   - kociemba: 用于求解魔方
   - Rubik's Cube：浏览器插件

### 整体思路

1. 计算魔方的小面位置
2. 识别魔方状态
3. 根据魔方状态计算公式
4. 将公式实现为电脑操作

### 原理细节
1. 获取小面位置
   - 获取一点位置 + 一边长度，则整个魔方的位置确定
      <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128172937.png" width = "100%">
   - 计算基本向量，以及 27 个小面的位置
      <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128174645.png" width = "100%">

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
   - 将正视图的三面视为 `U, L, F`，截图识别颜色分布
      <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/20220129130859.png" width="100%">
   - 滑动到背面，获取后三面的颜色分布
   - 两部分信息整合，导出魔方状态码

4. 魔方公式
   - 调用函数 `kociemba.solve` ，获取魔方公式
   - 魔方公式为 `U, U', U2, R, R', R2...` 等构成的列表
   - 其中 `U, U', U2` 分别代表顶面顺时针旋转 90°，逆时针旋转 90°，以及旋转旋转 180°，其他各面规则同理
   
5. 将公式实现为操作
   - 由小面位置和基本向量计算位置参数
   - 用 pyautogui 的函数 `moveTo` 和 `dragRel` 实现鼠标移动和拖拽

由于函数间需频繁共享位置数据，因而使用面向对象编程，数据作为属性，函数作为方法。

## 使用介绍
### 安装依赖
仅介绍 Ubuntu 系统的安装方法，其他系统类似
1. 安装 Python 包
   ```bash
   pip install pyautogui # 安装自动化工具
   pip install kociemba # 安装魔方工具
   ```

2. 安装 scrot，用于截图
   ```bash
   sudo apt-get install scrot
   ```

3. 在 Chrome 浏览器的应用商场，搜索 `rubik` 并安装插件
    ![深度截图_选择区域_20220128171120](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/深度截图_选择区域_20220128171120.png)

### 基本使用
工具包提供了这几个函数：
1. 初始化类对象
   ```py
   from rubik import *
   cube = Cude(standard=False)
   ```

2. 检查 27 个小面位置
   ```py
   cube.check_facets()
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/check_facets.gif" width="90%">

3. 检查魔方的基本旋转
   ```py
   cube.check_basic_moves() # 检查基本旋转是否正确
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/check_moves.gif" width="90%">

4. 获取魔方分布信息，并打印魔方展开图
   ```py
   # 获取小面分布信息
   state = cube.get_cube_distribution(string_code=True) 
   print(expand_cube(state))
   ```

5. 自动识别并求解魔方
   ```py
   cube.auto_solve_cube()
   ```
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/end.gif" width= "100%">

6. 根据魔方代码，构造给定的魔方状态
   ```py
   state = "UBRLUFFUBLRUFRLLLRDBDRFDBBUDDBUDDLRFBFLDLBFFRFLRUBRDUU"
   cube.to_cube_state(state)
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/to_state.gif" width="90%">

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
这是随手写的实战项目，还欠缺规范性；比如没有添加 CI/CD，帮助文档，文件系统也没有添加 Python 包常见的 `__init__.py` 等。这些将在后续进一步学习后，再改进和提升。