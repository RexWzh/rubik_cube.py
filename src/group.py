# 魔方群置换
permdict = {
    'U':[2, 4, 7, 1, 6, 0, 3, 5, 16, 17, 18, 11,
         12, 13, 14, 15, 32, 33, 34, 19, 20, 21, 22, 23,
         24, 25, 26, 27, 28, 29, 30, 31, 40, 41, 42, 35,
         36, 37, 38, 39, 8, 9, 10, 43, 44, 45, 46, 47],
    'R':[0, 1, 45, 3, 43, 5, 6, 40, 10, 12, 15, 9,
        14, 8, 11, 13, 16, 17, 2, 19, 4, 21, 22, 7,
        24, 25, 18, 27, 20, 29, 30, 23, 32, 33, 34, 35,
        36, 37, 38, 39, 31, 41, 42, 28, 44, 26, 46, 47],
    'F':[0, 1, 2, 3, 4, 8, 11, 13, 26, 9, 10, 25,
         12, 24, 14, 15, 18, 20, 23, 17, 22, 16, 19, 21,
         34, 36, 39, 27, 28, 29, 30, 31, 32, 33, 7, 35,
         6, 37, 38, 5, 40, 41, 42, 43, 44, 45, 46, 47],
    'D':[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 
         12, 45, 46, 47, 16, 17, 18, 19, 20, 13, 14, 15, 
         26, 28, 31, 25, 30, 24, 27, 29, 32, 33, 34, 35, 
         36, 21, 22, 23, 40, 41, 42, 43, 44, 37, 38, 39],
    'L':[16, 1, 2, 19, 4, 21, 6, 7, 8, 9, 10, 11,
         12, 13, 14, 15, 24, 17, 18, 27, 20, 29, 22, 23,
         47, 25, 26, 44, 28, 42, 30, 31, 34, 36, 39, 33,
         38, 32, 35, 37, 40, 41, 5, 43, 3, 45, 46, 0],
    'B':[37, 35, 32, 3, 4, 5, 6, 7, 8, 9, 0, 11,
         1, 13, 14, 2, 16, 17, 18, 19, 20, 21, 22, 23,
         24, 25, 26, 27, 28, 15, 12, 10, 29, 33, 34, 30,
         36, 31, 38, 39, 42, 44, 47, 41, 46, 40, 43, 45]
}

class GroupElement(object):
    def __init__(self, perm:list) -> None:
        self._unit = None
        if isinstance(perm, list):
            assert len(perm) == 48, "The length of the permutation must be 48."
        elif isinstance(perm, str):
            ele = self.str2perm(perm)
            perm = ele.perm
        else:
            raise Exception("输入有误")
        self.perm = perm
        self.init_state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    
    def state(self):
        return self(self.init_state)
    
    def __mul__(self, ele):
        """
        The multiplication of two permutations.
        """
        # 位置 i 先被 perm2 作用，再被 perm1 作用
        perm1, perm2 = self.perm, ele.perm
        return GroupElement([perm1[perm2[i]] for i in range(48)])
    
    def __truediv__(self, ele):
        return self * ele.inv()
    
    def inv(self):
        pre = [None] * 48
        for i, j in enumerate(self.perm):
            pre[j] = i
        return GroupElement(pre)
        
    def __call__(self, state):
        """
        Apply the permutation to a state.
        """
        if isinstance(state, str):
            state = list(state)
        for i in range(49, 0, -9):
            state.pop(i)
        newstate = [None] * 48
        for i in range(48):
            newstate[self.perm[i]] = state[i]
        for i, c in zip(range(4, 54, 9), "URFDLB"):
            newstate.insert(i, c)
        return ''.join(newstate)
    
    @staticmethod
    def _char2perm(c:str):
        assert len(c) == 1, "字符长度必须为 1"
        return GroupElement(permdict[c])
    
    def str2perm(self, st:str):
        eles = []
        for c in st:
            if c in "UFDLBR":
                eles.append(self._char2perm(c))
            elif c == "'": # inverse operation
                eles[-1] = eles[-1].inv()
            elif c == '2':
                eles[-1] *= eles[-1]
            else:
                raise Exception("Invalid string.")
        return self.prod(eles)
    
    def prod(self, eles):
        if len(eles) == 0:
            return self.unit
        ele = eles[0]
        for i in eles[1:]:
            ele *= i
        return ele
    
    def __repr__(self):
        return self.perm.__repr__()
    
    def __str__(self):
        return self.perm.__str__()
    
    def __xor__(self, n:int):
        if n == 0:return self.unit
        ele = self if n > 0 else self.inv()
        return self.prod([ele] * abs(n))
    
    @property
    def unit(self):
        if self._unit is None:
            self._unit = GroupElement(list(range(48)))
        return self._unit
    
    def isunit(self):
        return self == self.unit
    
    def __eq__(self, ele):
        return self.perm == ele.perm
    
    def order(self):
        assert len(set(self.perm)) == 48, "无效元素"
        n = 1
        ele = self
        while ele != self.unit:
            ele *= self
            n += 1
        return n