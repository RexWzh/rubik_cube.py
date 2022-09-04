import pyautogui as pg
import kociemba as kb
import numpy as np
import time, cv2
from data import template_path, color_to_facet
from tools import PIL2cv, check_positions, find_color, array_to_tuple, facets_to_tuple
from scale_match import scale_match, show_image, draw_rectangle
from group import GroupElement

template = cv2.imread(template_path)
if template is None:
    template = cv2.imread("../src/" + template_path)
if template is None:
    template = cv2.imread("./src/" + template_path)
assert template is not None, "未能读取模板文件，请在 src/ 目录下运行代码！"

class Cube():
    def __init__(self, interval:float = 0.2):
        """初始化

        Args:
            interval (float, optional): 操作的时间间隔. Defaults to 0.13.
        
        初始化内容：
           - 图像正中心位置，以及三个方向： center, left, right, down
           - 三个魔方面的小面位置： lefts, rights, ups
           - 运算需要的数值信息（字典）： operate_dict
           - 运算的时间间隔： interval
        """
        self._cube_dectection()
        self._init_facet_positions()
        self._init_operate_dict()
        self.interval = interval # 操作时间间隔
    
    def auto_solve_cube(self, wait=True):
        """自动求解魔方
        
        Args:
            wait (bool, optional): wait for input. Defaults to True.
        """
        cube_code = self.get_cube_distribution(string_code = True)
        print("魔方识别完毕")
        solution = kb.solve(cube_code).split()
        print("还原需要 %d 步"%len(solution))
        time.sleep(.4)
        if wait:
            input("按回车开始还原魔方")
        for op in solution:
            self.cube_operate(op)
        print("魔方已还原，请检查")
        return solution
        
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
    
    def check_basic_moves(self, facets:str = None) -> None:
        """检验基础旋转操作是否正确
        
        Args:
            faces (str, optional): 需要检查的魔方面. 默认检查所有面.
        """
        if facets is None:
            facets = "UDLRFB"
        for op in facets:
            print("当前正在旋转的面为", op)
            for i in ["", "'", "2"]:
                self.cube_operate(op + i)
                time.sleep(0.5)
        return 
    
    def show_dectition(self):
        """显示检查到的图像"""
        show_image(draw_rectangle(self.image, template.shape, self.Loc, self.ratio))
        
    ## 函数工具 ##
    def color_distribution(self, im, shift = False, abbr = True):
        """获取截图三面的颜色分布
        
        Args:
            im (PIL.PngImagePlugin.PngImageFile): 截图图像
            shift (bool, optional): 当前魔方是否为翻转后的魔方. Defaults to False.
            abbr (bool, optional): 是否返回简写(UDFBLR). Defaults to True.
        """
        face_U = [find_color(im, p) for p in self.ups]
        face_L = [find_color(im, p, 1) for p in self.lefts]
        face_F = [find_color(im, p, 2) for p in self.rights]
        if abbr:
            face_U, face_L, face_F = [[color_to_facet[i] for i in facets] for facets in [face_U, face_L, face_F]]
        if not shift: # 初始界面
            return face_U, face_L, face_F
        # 扭转后的界面
        face_B, face_R, face_D = face_U, [face_L[i-1] for i in (7,4,1,8,5,2,9,6,3)], face_F[::-1]
        return face_B, face_R, face_D
    
    def get_cube_distribution(self, string_code=False) -> list:
        """获取魔方的分布信息

        Args:
            string_code (bool, optional): 是否返回魔方字符代码. 默认返回字符代码构成的列表
        Returns:
            list/string: 返回字符列表，或者字符串
        """
        img = pg.screenshot() # 截图
        U, L, F = self.color_distribution(img) # 获取初始三面
        self.shift_faces() # 切换背面
        time.sleep(0.5)
        img = pg.screenshot()
        B, R, D = self.color_distribution(img, shift=True) # 获取背面
        self.shift_faces(back=True) # 切回原来面
        if string_code:
            return "".join(U) + "".join(R) + "".join(F) + "".join(D) + "".join(L) + "".join(B)
        return U, L, F, B, R, D
    
    def shift_faces(self, back=False) -> None:
        """左滑和上移，将魔方切换到背面
        
        Args:
           back (bool, optional): 是否从背面返回正面，默认从正面到背面
        """
        d = int(self.down[1])
        corner = array_to_tuple(self.center + (3 * d, 3 * d))
        seq = [(-d, 0), (-d, 0), (0, -d)] if not back else [(0, d), (d, 0), (d, 0)]
        for i, j in seq:
            pg.moveTo(corner, duration=0.1)
            pg.dragRel(i, j, duration=0.25)
        return
    
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
            pg.dragRel(rel[0], rel[1], duration=interval)
            pg.moveTo(pos)
            pg.dragRel(rel[0], rel[1], duration=interval)
        elif op[-1] == "'":
            pg.dragRel(-rel[0], -rel[1], duration=interval)
        else:
            pg.dragRel(rel[0], rel[1], duration=interval)
        return 
    
    def shift_center(self, back=False):
        """换心公式
        
        Args:
           back (bool, optional): 是否使用逆公式，默认否
        """
        center = self.ups[4]
        left, right = self.left, self.right
        if not back:
            seq = [array_to_tuple(i) for i in [left, right, -left, -right]]
        else:
            seq = [array_to_tuple(i) for i in [right, left, -right, -left]]
        for p in seq:
            pg.moveTo(center)
            pg.dragRel(p[0], p[1], duration = 0.25)
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
        assert (targetact.inv() * curact)(curstate) == state
        # 过渡状态
        mixstate = (curact.inv() * targetact).state()
        mixsol = kb.solve(mixstate).split() # 获取解法
        mixact = GroupElement(''.join(mixsol[::-1]))
        assert mixact(curstate) == state
        print("将魔方化为给定状态，步数", len(mixsol))
        for op in mixsol:
            self.cube_operate(op)
        self.get_cube_distribution()
        return mixsol

    def _cube_dectection(self):
        """检测魔方位置信息"""
        self.image = image = PIL2cv(pg.screenshot())
        _, Loc, ratio = scale_match(image, template, show=False)
        l1 = 200 * ratio
        l2, l3 = l1 * 208 // 246, l1 * 122 // 246
        self.left, self.right, self.down = [np.array(p) // 3 for p in [[-l2, -l3], [l2, -l3], [0, l1]]]
        self.center = ratio * np.array([Loc[0]+188, Loc[1] + 200])
        self.Loc, self.ratio = Loc, ratio

    def _init_facet_positions(self):
        """初始化上，左，右，三面的小面位置"""
        center, left, right, down = self.center, self.left, self.right, self.down
        left_origin, right_origin, up_origin = [center + i // 2 for i in [left + down, right + down, left + right]]
        lefts = [[left_origin + (2 - i) * left + j * down for i in range(3)] for j in range(3)]
        rights = [[right_origin + i * right + j * down for i in range(3)] for j in range(3)]
        ups = [[up_origin + i * right + (2 - j) * left for i in range(3)]for j in range(3)]
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