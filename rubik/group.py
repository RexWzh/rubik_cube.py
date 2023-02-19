import kociemba as kb

# 魔方群置换
class GroupElement(object):
    def __init__(self, perm):
        self._unit = None
        if isinstance(perm, list):
            assert len(perm) == 48, "The length of the permutation must be 48."
        elif isinstance(perm, str): 
            ele = self.str2perm(perm)
            perm = ele.perm
        else:
            raise Exception("Invalid type of the permutation.")
        self.perm = perm
        self.init_state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    
    def state(self):
        """cube state of the permutation

        Returns:
            str: image of the action.
        """
        return self(self.init_state)
    
    @staticmethod
    def _char2perm(c:str):
        assert len(c) == 1, "The length of the character must be 1."
        return GroupElement(permdict[c])
    
    def str2perm(self, st:str):
        """Convert a string to a permutation.

        Args:
            st (str): the string.

        Raises:
            Exception: invalid string.

        Returns:
            GroupElement: the permutation.
        """
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
    
    def __mul__(self, ele):
        """Compose two permutations.

        Args:
            ele (GroupElement): another permutation.

        Returns:
            GroupElement: the composition of two permutations.
        """
        # act first by perm2 then by perm1
        perm1, perm2 = self.perm, ele.perm
        return GroupElement([perm1[perm2[i]] for i in range(48)])
    
    def __truediv__(self, ele):
        """The quotient of two permutations.

        Args:
            ele (GroupElement): another permutation.

        Returns:
            GroupElement: the quotient of two permutations.
        """
        return self * ele.inv()
    
    def inv(self):
        """Inverse of the permutation.

        Returns:
            GroupElement: inverse of the permutation.
        """
        pre = [None] * 48
        for i, j in enumerate(self.perm):
            pre[j] = i
        return GroupElement(pre)
        
    def __call__(self, state):
        """Image of the action of the permutation on the state.

        Args:
            state (str): the state.

        Returns:
            str: image of the action.
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
    
    def prod(self, eles):
        """Product of a list of permutations.

        Args:
            eles (list): list of permutations.

        Returns:
            GroupElement: the product of the list of permutations.
        """
        if len(eles) == 0:
            return self.unit
        ele = eles[0]
        for i in eles[1:]:
            ele *= i
        return ele
    
    def __xor__(self, n:int):
        """n-th power of the permutation.

        Args:
            n (int): the power.

        Returns:
            GroupElement: n-th power of the permutation.
        """
        if n == 0:return self.unit
        ele = self if n > 0 else self.inv()
        return self.prod([ele] * abs(n))
    
    @property
    def unit(self):
        """The identity element.

        Returns:
            GroupElement: the identity element.
        """
        if self._unit is None:
            self._unit = GroupElement(list(range(48)))
        return self._unit
    
    def isunit(self):
        """Check if the permutation is the identity element.

        Returns:
            bool: True if the permutation is the identity element.
        """
        return self == self.unit
    
    def __eq__(self, ele):
        """Check if two permutations are equal.

        Args:
            ele (GroupElement): another permutation.

        Returns:
            bool: True if two permutations are equal.
        """
        return self.perm == ele.perm
    
    def order(self):
        """Order of the permutation.

        Returns:
            int: order of the permutation.
        """
        assert len(set(self.perm)) == 48, "The permutation is not a group element."
        n = 1
        ele = self
        while ele != self.unit:
            ele *= self
            n += 1
        return n

    def __repr__(self):
        return self.perm.__repr__()
    
    def __str__(self):
        return self.perm.__str__()

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

# 魔方中心置换
init_state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

default_centers = "URFDLB" # 上，右，前，下，左，后

valid_centers = [
    'URFDLB', 'ULBDRF', 'LBURFD',
    'LFDRBU', 'DLFURB', 'DRBULF',
    'RBDLFU', 'RFULBD', 'FURBDL',
    'FDLBUR', 'BULFDR', 'BDRFUL'
]
is_valid_center = lambda cen: cen in valid_centers

def shift_color(state:str, new_centers:str, skipcenter=False):
    """转化魔方上的颜色
    state: 魔方状态
    new_centers: 新的中心颜色
    skipcenter: 是否保留中心颜色
    """
    raw_centers = state[4::9]
    state = "".join(new_centers[raw_centers.index(i)] for i in state)
    if not skipcenter: return state
    state = list(state)
    state[4::9] = raw_centers
    return ''.join(state)

def standardize_center(state, check=True):
    """将魔方状态的颜色转化为标准形式"""
    cen = state[4::9]
    assert not check or is_valid_center(cen), "魔方中心颜色无效！"
    return shift_color(state, default_centers)

def is_valid_cube(state):
    if not is_valid_center(state[4::9]): return False
    try:
        kb.solve(state)
        return True
    except:
        return False