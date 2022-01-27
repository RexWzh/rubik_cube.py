# 用类编程处理数据
import numpy as np
import pyautogui as pg
import kociemba as kb
import time

# 颜色和小面位置相互转化（字典）
color_to_facet = {"white":"U", "red":"L", "blue":"F", "green":"B", "orange":"R", "yellow":"D"}
facet_to_color = {val:key for key, val in color_to_facet.items()}
# 上，左，右，处在三个位置时各颜色的数值
colors = {'white': ((252, 244, 252), (222, 215, 222), (198, 192, 198)),
         'red': ((236, 56, 35), (208, 50, 30), (186, 44, 27)),
         'blue': ((64, 168, 198), (56, 148, 174), (51, 132, 155)),
         'green': ((128, 200, 55), (113, 176, 49), (101, 157, 44)),
         'orange': ((252, 138, 10), (222, 122, 9), (198, 109, 8)),
         'yellow': ((252, 237, 71), (222, 208, 63), (198, 186, 56))}
# numpy 数组转化为元组
array_to_tuple = lambda arr:tuple(int(i) for i in arr)
# 小面集转化为元组
facets_to_tuple = lambda facets:[array_to_tuple(i) for line in facets for i in line]
# 比较两个颜色的差异
diff = lambda c1, c2: sum(abs(i - j) for i, j in zip(c1, c2))

def cube_initialize(standard: bool = True):
    """初始化魔方位置信息"""
    if standard: # 标准情形：图像置于左侧
        center, l1 = np.array([535, 669]), 290
    else: # 否则要求输入两个特定位置
        input("按回车录入中心点位置")
        center = np.array(pg.position())
        input("按回车录入底部位置")
        bottom = np.array(pg.position())
        l1 = bottom[1] - center[1]
        print("中心位置",center, "垂直长度", l1)
    l2, l3 = l1 * 208 // 246, l1 * 122 // 246
    left, right, down = [np.array(p) //3 for p in [[-l2, -l3], [l2, -l3], [0, l1]]]
    return center, left, right, down

def check_positions(positions):
    """鼠标依次移动到给定位置-用于检验小面中心正确性"""
    for p in positions:
        time.sleep(0.2)
        pg.moveTo(p)
    return 

def find_color(img, pos, side = 0):
    """
    匹配三维数组 color 对应的颜色
    side 参数如下：
       - 0 小面位于上方
       - 1 小面位于左侧
       - 2 小面位于右侧
    """
    color = img.getpixel(pos)
    return min(colors.keys(), key = lambda c: diff(colors[c][side], color))

def reverse_operation(op):
    """获取操作的逆运算"""
    if len(op) == 1:
        return op + "'"
    if op[-1] == "'":
        return op[0]
    return op

reverse_operations = lambda solution:[reverse_operation(op) for op in solution[::-1]]

class Cube():
    def __init__(self, standard=True):
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