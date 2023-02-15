# 魔方自动还原

**工具原理及使用演示**： [一行代码“玩转”魔方 | Python](https://www.bilibili.com/video/BV1yU4y1B71P)

在 B 站看到一个用 Python 复原魔方的[视频](https://www.bilibili.com/video/BV12i4y1G74V)，觉得还蛮有意思，就自己动手写了个工具。废话不多说，先看演示吧。

1. 随机打乱一个魔方
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/start.gif" width= "100%">

2. 导入工具，一行代码还原魔方
   ```py
   from rubik import *
   Cube().auto_solve_cube(wait=False)
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/end.gif" width= "100%">

---

## 使用介绍
### 安装依赖

1. 安装 Python 包
   ```bash
   pip install pyautogui # 自动化工具
   pip install kociemba # 魔方算法工具
   pip install opencv-python # 图像处理工具
   pip install imutils # 图像放缩
   ```

2. 搜索安装谷歌浏览器的插件 `Rubik`
    ![深度截图_选择区域_20220128171120](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/深度截图_选择区域_20220128171120.png)

3. Ubuntu 系统还需要安装 scrot 用于截图
   ```bash
   sudo apt-get install scrot
   ```

4. Mac 系统需开启屏幕截图权限，否则只会截取桌面，参见 [StackOverflow](https://stackoverflow.com/questions/63947364/pyautogui-screenshots-my-only-background-mac-os)。

### 使用方法

> 特别说明：`<仓库>/demo` 目录下有两个 Jupyter 文件，其中 `demo-jupyter.ipynb` 用于演示和错误调试，`比利比利.ipynb` 为[ B 站视频](https://www.bilibili.com/video/BV1yU4y1B71P) 使用的代码。

1. 打开浏览器插件，双击进入准备状态
   ![20220419174040](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/20220419174040.png)

2. 初始化类对象 `Cube`，检测魔方位置
   ```py
   from rubik import *
   cube = Cude()
   ```

3. 查看魔方定位是否正确
   ```py
   cube.show_detection()
   ```
   ![output](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/output.jpg)
   

4. 检查小面位置
   ```py
   cube.check_facets()
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/check_facets.gif" width="90%">

5. 检查基本旋转
   ```py
   cube.check_basic_moves() # 检查基本旋转是否正确
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/check_moves.gif" width="90%">

6. 识别魔方状态，并打印展开图
   ```py
   # 获取小面分布信息
   state = cube.get_cube_distribution(string_code=True) 
   print(expand_cube(state))
   ```

7. 识别并求解魔方
   ```py
   cube.auto_solve_cube()
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/end.gif" width= "100%">

8. 构造给定魔方状态
   ```py
   state = "UBRLUFFUBLRUFRLLLRDBDRFDBBUDDBUDDLRFBFLDLBFFRFLRUBRDUU"
   cube.to_cube_state(state)
   ```
   <img src="http://qiniu.wzhecnu.cn/cube/to_state.gif" width="90%">

### 文件说明

1. `src` 目录下有五个主要文件
   | 文件名 | 说明介绍 |
   | :---: | :-----: |
   | `rubik.py` | 类对象 `Cube` |
   | `group.py` | 魔方群工具 |
   | `tools.py` | 函数工具 |
   | `data.py` | 记录魔方的色块等信息 |
   | `scale_match.py` | 支持比例放缩的图像检测 |
   
2. `demo` 目录下
   | 文件名 | 说明介绍 |
   | :---: | :-----: |
   | `demo.jupyter` | 演示文档 |
   | `quick_start.py` | 快捷调用|

---

## 工具原理
分两部分：
   - `pyautogui + cv2` 检测魔方位置，识别魔方状态，执行电脑操作
   - `kociemba` 调用魔方算法

此外，函数 `Cube.to_cube_state()` 借助群论，扩展 Kociemba 算法的使用范围，也即用于魔方状态的转换，而不局限于魔方还原。

### 原理细节
1. 图像检测，计算最佳比例和魔方位置
   ![test](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/test.gif)

2. 计算一点 + 一边，并推导其他位置信息
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128172937.png" width = "100%">

3. 魔方状态码
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

4. 识别魔方状态：
   - 将正视图的三面视为 `U, L, F`，截图识别颜色分布
      <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed2/picgo/20220129130859.png" width="100%">
   - 滑动到背面，获取后三面的颜色分布
   - 两部分信息整合，导出魔方状态码

5. 魔方公式
   - 调用函数 `kociemba.solve` ，获取魔方公式
   - 魔方公式为 `U, U', U2, R, R', R2...` 等构成的列表
   - 其中 `U, U', U2` 分别代表顶面顺时针旋转 90°，逆时针旋转 90°，以及旋转旋转 180°，其他各面规则同理
   
6. 将公式实现为操作
   - 由小面位置和基本向量计算位置参数
   - 用 pyautogui 的函数 `moveTo` 和 `dragRel` 实现鼠标移动和拖拽

由于函数间需频繁共享位置数据，因而使用面向对象编程，数据作为属性，函数作为方法。

---

## 写在最后
这是放假在家随手写的实战，代码在 Ubuntu 和 Windows 测试通过，如果遇到问题欢迎评论交流~

