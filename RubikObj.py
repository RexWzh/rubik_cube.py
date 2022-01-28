import pyautogui as pg
import kociemba as kb
import time
from tools import *


class Cube():
    def __init__(self, standard=True):
        """[summary]

        Args:
            standard (bool, optional): [description]. Defaults to True.
        """
        self.center, self.left, self.right, self.down = cube_initialize(standard)
        self.init_facet_positions()
        self.init_operate_dict()
        self.interval = 0.13 # 操作时间间隔
    
    def init_facet_positions(self):
        """初始化左，右，上，三面的小面位置"""
        center, left, right, down = self.center, self.left, self.right, self.down
        left_origin, right_origin, up_origin = [center + i // 2 for i in [left + down, right + down, left + right]]
        lefts = [[left_origin + (2 - i) * left + j * down for i in range(3)] for j in range(3)]
        rights = [[right_origin + i * right + j * down for i in range(3)] for j in range(3)]
        ups = [[up_origin + i * right + (2 - j) * left for i in range(3)]for j in range(3)]
        self.lefts = facets_to_tuple(lefts)
        self.rights = facets_to_tuple(rights)
        self.ups = facets_to_tuple(ups)
        return
    
    def init_operate_dict(self):
        """初始化基础运算信息"""
        lefts, rights, ups = self.lefts, self.rights, self.ups
        left, right, down = self.left, self.right, self.down
        self.operate_dict = {"U":(lefts[1], array_to_tuple(left)),
         "F":(lefts[5], array_to_tuple(-down)),
         "L":(rights[3], array_to_tuple(down)),
         "D":(rights[7], array_to_tuple(right)),
         "B":(ups[1], array_to_tuple(-right)),
         "R":(ups[5], array_to_tuple(left))}
        return 
        
    def auto_solve_cube(self, ask=True):
        """自动求解魔方"""
        cube_code = self.get_cube_distribution(string_code = True)
        print("魔方识别完毕")
        solution = kb.solve(cube_code).split()
        print("一共需要 %d 步"%len(solution))
        if ask:
            input("按回车开始还原魔方")
        for op in solution:
            self.cube_operate(op)
        return solution
    
    
    ## 检查数据 ##
    def check_facets(self, sides = None):
        """检验小面位置，sides 0,1,2 分别对应顶面，左面，右面"""
        if sides is None:
            sides = (0, 1, 2)
        if 0 in sides:
            check_positions(self.ups)
        if 1 in sides:
            check_positions(self.lefts)
        if 2 in sides:
            check_positions(self.rights)
        return 
    
    def check_basic_moves(self):
        """检验六个面的基础操作是否正确"""
        for op in "UDLRFB":
            print("当前面为", op)
            for i in ["", "'", "2"]:
                self.cube_operate(op + i)
                time.sleep(0.5)
        return 
    
    ## 函数工具 ##
    def color_distribution(self, im, shift = False, abbr = True):
        """获取截图三面的颜色分布，shift 获取移动后的颜色分布，abbr 设置是否用简写输出(UDFBLR)"""
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
        
    def get_cube_distribution(self, string_code=False):
        """获取魔方的分布信息，默认返回列表，可设置返回魔方字符"""
        img = pg.screenshot() # 截图
        U, L, F = self.color_distribution(img) # 获取初始三面
        self.shift_faces() # 切换背面
        time.sleep(1)
        img = pg.screenshot()
        B, R, D = self.color_distribution(img, shift=True) # 获取背面
        self.shift_faces(back=True) # 切回原来面
        if string_code:
            return "".join(U) + "".join(R) + "".join(F) + "".join(D) + "".join(L) + "".join(B)
        return U, L, F, B, R, D
    
    def shift_faces(self, back=False):
        """左滑和上移"""
        d = int(self.down[1])
        corner = array_to_tuple(self.center + (3 * d, 3 * d))
        seq = [(-d, 0), (-d, 0), (0, -d)] if not back else [(0, d), (d, 0), (d, 0)]
        for i, j in seq:
            pg.moveTo(corner, duration=0.1)
            pg.dragRel(i, j, duration=0.25)
        return
    
    def cube_operate(self, op):
        """将魔方字符转为具体操作"""
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
        """换心公式"""
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
    
    def to_cube_state(self, state):
        """将状态化为给定状态"""
        current = self.get_cube_distribution(string_code = True)
        current_sol = kb.solve(current).split()
        state_sol = kb.solve(state).split()
        reverse_sol = reverse_operations(state_sol)
        print("正在移位中心")
        self.shift_center()
        print("正在将魔方“还原”")
        for op in current_sol:
            self.cube_operate(op)
        print("将魔方化为给定状态")
        for op in reverse_sol:
            self.cube_operate(op)
        print("最后还原中心")
        self.shift_center(back=True)
        return state_sol

### 补充字符相关的操作和运算