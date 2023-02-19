__version__ = "0.1.0"

import pyautogui as pg
import kociemba as kb
import numpy as np
import time, cv2
from rubik.data import template_path, color_table
from rubik.tools import PIL2cv, check_positions, array_to_tuple, facets_to_tuple, cv2PIL, expand_cube, screenshot, face_rotate
from rubik.scale_match import detect_image, show_image, draw_rectangle
from rubik.group import GroupElement, is_valid_cube

template = cv2.imread(template_path)
assert template is not None, "未能读取模板文件！"

class Cube():
    def __init__(self, interval:float = 0.2, updatecolor=False, checkcolor=False):
        """初始化

        Args:
            interval (float, optional): 操作的时间间隔. Defaults to 0.13.
        
        初始化内容：
           - 图像正中心位置，以及三个方向： center, left, right, down
           - 三个魔方面的小面位置： lefts, rights, ups
           - 运算需要的数值信息（字典）： operate_dict
           - 运算的时间间隔： interval
        """
        self._cube_detection()
        self._init_facet_positions()
        self._init_operate_dict()
        if not updatecolor:
            self._color_table = color_table
        else:
            self.update_colortable(check=checkcolor)
        self.interval = interval # 操作时间间隔
    
    def auto_solve_cube(self, state=None, wait=True):
        """自动求解魔方
        
        Args:
            wait (bool, optional): wait for input. Defaults to True.
        """
        # 识别魔方
        if state is None:
            cube_code = self.get_cube_distribution(string_code = True)
        else:
            cube_code = state
        print("魔方识别完毕")
        solution = self.solvebykociemba(cube_code)
        print("还原需要 %d 步"%len(solution))
        time.sleep(.4)
        if wait:
            input("按回车开始还原魔方")
        # 还原魔方
        self._move2center()
        for op in solution:
            self.cube_operate(op)
        print("魔方已还原，请检查")
        return solution
    
    @staticmethod
    def solvebykociemba(cube_code:str) -> list:
        """使用 kociemba 库求解魔方
        
        Args:
            cube_code (str): 魔方状态
        
        Returns:
            list: 魔方还原步骤
        """
        try:
            sol = kb.solve(cube_code)
        except:
            print("魔方状态码无效，可能存在颜色错误，请校对魔方展开图")
            print(expand_cube(cube_code))
            raise ValueError("魔方状态错误，无法还原")
        return sol.split()

    ## 检查数据 ##
    def check_facets(self, sides = None) -> None:
        """检验小面位置

        Args:
            sides (list(int) or int, optional): 需要检查的魔方面. 默认检查三个面.

        Returns:
            None: 不返回值
        
        说明：
           - 列表 sides 中， 0,1,2 分别对应顶面，左面，右面
        """
        if sides is None:
            sides = [0, 1, 2]
        elif isinstance(sides, int):
            sides = [sides]
        if 0 in sides:
            print("正在检查顶面，注意查看鼠标位置是否准确")
            check_positions(self.ups)
        if 1 in sides:
            print("正在检查左侧面，注意查看鼠标位置是否准确")
            check_positions(self.lefts)
        if 2 in sides:
            print("正在检查右侧面，注意查看鼠标位置是否准确")
            check_positions(self.rights)
        return 
    
    ## 检查中心
    def check_center(self, click=False) -> None:
        """检查中心位置"""
        print("检查鼠标是否移动到中心位置")
        self._move2center(click=click)
        return

    def check_basic_moves(self, facets:str = None) -> None:
        """检验基础旋转操作是否正确
        
        Args:
            faces (str, optional): 需要检查的魔方面. 默认检查所有面.
        """
        if facets is None:
            facets = "UDLRFB"
        self._move2center()
        for op in facets:
            print("当前正在旋转的面为", op)
            for i in ["", "'", "2"]:
                self.cube_operate(op + i)
                time.sleep(0.5)
        return 
    
    def shift_center(self, back=False):
        """换心公式
        
        Args:
           back (bool, optional): 是否使用逆公式，默认否
        """
        self._move2center()
        center = self.ups[4]
        left, right = self.left, self.right
        if not back:
            seq = [array_to_tuple(i) for i in [left, right, -left, -right]]
        else:
            seq = [array_to_tuple(i) for i in [right, left, -right, -left]]
        for p in seq:
            pg.moveTo(center)
            pg.dragRel(p[0], p[1], duration = 0.25, button="left")
        return
    
    def show_detection(self, openwindow = True):
        """显示检查到的图像"""
        if openwindow:
            show_image(draw_rectangle(self.image, template.shape, self.Loc, self.ratio))
        else:
            return cv2PIL(draw_rectangle(self.image, template.shape, self.Loc, self.ratio))
        return
    
    def get_cube_distribution(self, string_code=False) -> list:
        """获取魔方的分布信息

        Args:
            string_code (bool, optional): 是否返回魔方字符代码. 默认返回字符代码构成的列表
        Returns:
            list/string: 返回字符列表，或者字符串
        """
        self._move2center()
        # 获取正面颜色分布
        img = screenshot() # 截图
        ULF = self._read_pixels_of_ULF(img) # 获取像素值
        U, L, F = [[self.pixel2color(pix, i) for pix in face] for i, face in enumerate(ULF)]
        # 切换背面并获取分布
        self.shift_faces()
        time.sleep(0.5)
        img = screenshot()
        BRD = self._read_pixels_of_ULF(img, rotates=(0, 1, 2))
        B, R, D = [[self.pixel2color(pix, i) for pix in face] for i, face in enumerate(BRD)]
        self.shift_faces(back=True)
        # 切回原来面，并返回识别结果
        if string_code:
            return "".join(U) + "".join(R) + "".join(F) + "".join(D) + "".join(L) + "".join(B)
        return U, L, F, B, R, D
    
    def shift_faces(self, back=False) -> None:
        """左滑和上移，将魔方切换到背面
        
        Args:
           back (bool, optional): 是否从背面返回正面，默认从正面到背面
        """
        seq = "LLU" if not back else "DRR"
        for op in seq:
            self._shift_direction(op)
        return
    
    def to_cube_state(self, state: str = None) -> list:
        """将打乱的魔方化为给定魔方状态，并求解
        
        Args:
           state (str): 给定魔方状态的字符代码
        
        Returns:
           list(str): 返回给定魔方状态的解法
        
        """
        if state is None:
            state = "DUDUUUDUDBRBRRRBRBLFLFFFLFLUDUDDDUDUFLFLLLFLFRBRBBBRBR"
        # 当前状态
        curstate = self.get_cube_distribution(string_code = True)
        cursol = kb.solve(curstate).split()[::-1] # 当前解法(作用从左到右，需反转)
        curact = GroupElement(''.join(cursol)) # 转化为群元素 action
        # 目标状态
        targetsol = kb.solve(state).split()[::-1]
        targetact = GroupElement(''.join(targetsol))
        assert (targetact.inv() * curact)(curstate) == state, "计算有误！"
        # 过渡状态
        mixstate = (curact.inv() * targetact).state()
        mixsol = kb.solve(mixstate).split() # 获取解法
        mixact = GroupElement(''.join(mixsol[::-1]))
        assert mixact(curstate) == state, "计算有误！"
        print("将魔方化为给定状态，步数", len(mixsol))
        for op in mixsol:
            self.cube_operate(op)
        self.shift_faces()
        self.shift_faces(back=True)
        return mixsol

    def update_colortable(self, check=False):
        """更新魔方颜色"""
        faces = self._get_pixels_of_six_faces()
        cens = [[face[4] for face in side] for side in faces]
        self._color_table = dict(
            (face, tuple(cens[j][i] for j in range(3))) for i, face in enumerate("URFDLB"))
        # OPTIONAL: 颜色取均值，增加准确性
        if check:
            assert self._test_colors(faces=faces), "颜色识别有误"
        return self._color_table

    def pixel2color(self, pix, side=0) -> str:
        """返回与像素最匹配的颜色

        Args:
            pix (tuple(int, int, int)): 像素值
            side (int, optional): 像素所在位置. Defaults to 0.

        Returns:
            str: 匹配到的颜色，比如 white
        
        补充说明：
        1. side 参数如下：
            - 0 小面位于上方
            - 1 小面位于左侧
            - 2 小面位于右侧
        2. Google 插件的魔方图像中，同色块在三个方向的像素有较大区别，所以匹配所在面的颜色信息，增加准确性。
        """
        diff = lambda c1, c2: sum(abs(i - j) for i, j in zip(c1, c2))
        color = self._color_table
        return min(color.keys(), key = lambda c: diff(color[c][side], pix))

    def faces2state(self, faces, side=0):
        """像素值转为魔方状态"""
        state = ""
        for face in faces:
            state += ''.join(self.pixel2color(pix, side=side) for pix in face)
        return state

    def cube_operate(self, op):
        """将魔方字符转为具体操作
        
        Args:
           op (str): 魔方操作的字符代码
        """
        assert len(op) <= 2, "指令有误"
        operate_dict, interval = self.operate_dict, self.interval
        pos, rel = operate_dict[op[0]] # 位置以及相对位移
        pg.moveTo(pos)
        if op[-1] == "2":
            pg.dragRel(rel[0], rel[1], duration=interval, button="left")
            pg.moveTo(pos)
            pg.dragRel(rel[0], rel[1], duration=interval, button="left")
        elif op[-1] == "'":
            pg.dragRel(-rel[0], -rel[1], duration=interval, button="left")
        else:
            pg.dragRel(rel[0], rel[1], duration=interval, button="left")
        return 
    
    def _shift_direction(self, direct:str)-> None:
        """左滑/右滑/上移/下移

        Args:
            direct (str): 滑动方向，L/R/U/D
        """
        assert direct in "LRUD" and len(direct) == 1, "指令有误"
        corner, str2loc = self.corner, self.str2loc
        pg.moveTo(corner, duration=0.1)
        pg.dragRel(*str2loc[direct], duration=0.25, button="left")
        return 
    
    def _test_colors(self, faces=None):
        if faces is None:
            faces = self._get_pixels_of_six_faces()
        states = [self.faces2state(face, side=i) for i, face in enumerate(faces)]
        if not states[0] == states[1] == states[2]:
            return False
        return is_valid_cube(states[0])
    
    def _read_pixels_of_ULF(self, img=None, rotates = None):
        """获取魔方三个面的像素值
        
        变量 rotate 用于修正魔方的旋转
        """
        if img is None:
            img = self.image_pil
        if rotates is None:
            rotates = [0, 0, 0]
        rotates = [r % 4 for r in rotates] # mod 4
        ULF = [[img.getpixel(loc)[:3] for loc in locs] for locs in [self.ups, self.lefts, self.rights]]
        return [face_rotate(face, r) for face, r in zip(ULF, rotates)]
    
    def _get_pixels_of_six_faces(self):
        """获取魔方六个面不同方向的图像"""
        def _leftdown(rotates=None):
            self._shift_direction("L")
            self._shift_direction("D")
            img = screenshot()
            return self._read_pixels_of_ULF(img, rotates=rotates)
        
        self._move2center()
        # 一共截六次图，每次截图三个面，共 18 个面
        faces = [None] * 6
        # 正视图
        img = screenshot() # 标准图
        U0, L1, F2 = self._read_pixels_of_ULF(img, rotates=(0, 0, 0)) # 获取初始三面
        L0, F1, U2 = _leftdown(rotates=(2, 3, 3)) # 顺时针 120°
        F0, U1, L2 = _leftdown(rotates=(1, 2, 1)) # 顺时针 240°
        # 切换背面
        self.shift_faces()
        time.sleep(0.5)
        # 反视图
        img = screenshot()
        R0, D1, B2 = self._read_pixels_of_ULF(img, rotates=(3, 1, 3)) # 获取背面
        D0, B1, R2 = _leftdown(rotates=(3, 2, 2)) # 顺时针 120°
        B0, R1, D2 = _leftdown(rotates=(0, 1, 2)) # 顺时针 240°
        self.shift_faces(back=True) # 切回原来面
        
        return [[U0, R0, F0, D0, L0, B0],
                [U1, R1, F1, D1, L1, B1],
                [U2, R2, F2, D2, L2, B2],]
    
    def _move2center(self, click=True):
        """将魔方移动魔方中心"""
        pg.moveTo(tuple(self.center))
        if click:
            pg.click()
        return
    
    def _cube_detection(self):
        """检测魔方位置信息"""
        img_pil = screenshot()
        image = PIL2cv(img_pil)
        self.image_pil, self.image = img_pil, image
        # 图像检测
        _, Loc, ratio = detect_image(image, template)
        l1 = 200 * ratio
        l2, l3 = l1 * 208 // 246, l1 * 122 // 246
        # 魔方三个中心小面的中心点
        self.left, self.right, self.down = [np.array(p) // 3 for p in [[-l2, -l3], [l2, -l3], [0, l1]]]
        # 魔方中心点
        self.center = ratio * np.array([Loc[0]+188, Loc[1] + 200])        
        # 魔方右下的角落
        unit = int(self.down[1]) # 单位长度
        self.corner = array_to_tuple(self.center + (3 * unit, 3 * unit))
        self.str2loc = {"L": (-unit, 0), "R": (unit, 0), "U": (0, -unit), "D": (0, unit)}
        # 最佳定位位置和比例
        self.Loc, self.ratio = Loc, ratio

    def _init_facet_positions(self):
        """初始化上，左，右，三面的小面位置"""
        center, left, right, down = self.center, self.left, self.right, self.down
        left_origin, right_origin, up_origin = [center + i // 2 for i in [left + down, right + down, left + right]]
        lefts = [[left_origin + (2 - i) * left + j * down for i in range(3)] for j in range(3)]
        rights = [[right_origin + i * right + j * down for i in range(3)] for j in range(3)]
        ups = [[up_origin + i * right + (2 - j) * left for i in range(3)] for j in range(3)]
        self.lefts = facets_to_tuple(lefts)
        self.rights = facets_to_tuple(rights)
        self.ups = facets_to_tuple(ups)
        return
    
    def _init_operate_dict(self):
        """初始化魔方基础运算需要的数据（字典）"""
        lefts, rights, ups = self.lefts, self.rights, self.ups
        left, right, down = self.left, self.right, self.down
        self.operate_dict = {"U":(lefts[1], array_to_tuple(left)),
         "F":(lefts[5], array_to_tuple(-down)),
         "L":(rights[3], array_to_tuple(down)),
         "D":(rights[7], array_to_tuple(right)),
         "B":(ups[1], array_to_tuple(-right)),
         "R":(ups[5], array_to_tuple(left))}
        return 