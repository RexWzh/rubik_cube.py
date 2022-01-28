## 基于图像识别的魔方自动还原


逛 B 站时，偶然看到[一个视频](https://www.bilibili.com/video/BV12i4y1G74V)，用 Python + 谷歌浏览器插件，实现魔方的自动还原。觉得这个想法还蛮有意思，就自己动手写了这个工具。

废话不多说，先来看一个演示吧。

### 演示例子
1. 随机打乱魔方
   <img src="http://qiniu.wzhecnu.xyz/cube/initial.gif" width= "60%">

2. 观察并还原魔方
   ```py
   from rubik import *
   Cube().auto_solve_cube(wait=False)
   ```
   <img src="http://qiniu.wzhecnu.xyz/cube/solve.gif" width= "60%">

借助这套工具，一行代码就可以“玩转”整个魔方。

---

## 编写方法
### 整体思路
1. 工具依赖两个 Python 包，以及一个浏览器插件：
   - pyautogui: 用于识别图像和执行操作
   - kociemba: 用 `kociemba` 算法求解魔方
   - Rubik's Cube 插件
    ![深度截图_选择区域_20220128171120](https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/深度截图_选择区域_20220128171120.png)

2. 编写分几个小步骤：
   1. 识别魔方位置，并计算小面位置
   2. 获取小面颜色，识别魔方状态
   3. 根据魔方状态，计算求解公式
   4. 将魔方公式的字符 "UDFBLR" + "'2" 翻译为图上操作，并依次执行

### 方法细节

1. 获取一点 + 一边，整个魔方的位置信息被确定
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128172937.png" width = "50%">

2. 通过计算三个基本向量，求得 27 个小面的位置
   <img src="https://cdn.jsdelivr.net/gh/zhihongecnu/PicBed/picgo/20220128174645.png" width = "50%">

3. 魔方代码中， `URFDLB` 分别是六个面的缩写
   - U 为顶面（up）
   - R 为右面（right）
   - F 为正面（Front）
   - D 为顶面（down）
   - L 为左面（Left）
   - B 为背面（Back）
   - 魔方状态用 `URFDLB` 构成的序列表示，并按下边展开图的顺序读入
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

4. 获取魔方状态，过程如下：
   - 将正视图“上，左，右”的三面视为 `U, L, F`，截图获取分布信息
   - 滑动到背面，获取后三面的分布信息，再滑动回来
   - 两部分结果整合，按魔方代码要求的次序导出状态字符串

5. 调用 `kociemba.solve` 求得魔方公式
   
6. 魔方公式中，`U, U', U2` 分别代表顶面顺时针旋转 90°，逆时针旋转 90°，以及旋转旋转 180°，其他各面规则同理。利用 pyautogui 的函数 `moveTo` 和 `dragRel` 将这些规则化为自动操作。
    