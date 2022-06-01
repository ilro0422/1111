import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
import pytest
from pySym.pyPathGroup import PathGroup

test1 = """
x = 7
y = 2
if x == y:
    print("One")
else:
    x {0} 7
"""

test2 = """
x = 7
y = 2.0
if x == y:
    print("One")
else:
    x += y
"""

test3 = """
a = 0x10325476
b = 0x98BADCFE
c = 0xEFCDAB89
d = 0x67452301
g = 0x12345678
e = a ^ g
e ^= b
e |= c
e >>= 5
e &= 0x12345678
e <<= 20
"""

test4 = """
h = pyState.BVV(1337,64)
h += 0xffffffffffffffff
"""

test5 = """
h = pyState.BVV(1337,64)
h *= 0xffffffffffffff
"""

test6 = """
h = pyState.BVV(1337,64)
h -= 1338
"""

test7 = """
def test(x,y):
    return x**y

x = 2
x **= test(2,4)
"""

test8 = """
x = 50%6
y = x%4
"""

test9 = """
l = [1,2.2,3]
l[1] += 5.5
"""

test10 = """
x = pyState.BVV(123,32)
y = pyState.BVV(4,32)
l = [1,x,3]
l[1] += y
"""

test11 = """
l = [1,2,3]
l[1] += 2
"""

test12 = """
x = pyState.BVV(5,32)
l = [1,x,3]
l[1] ^= 2
"""

test13 = """
s = pyState.String(10)
x = 1
x += s.index("b")
"""

test14 = """
l = ["a","b","c"]
l[1] += "d"
l[1] += "E"
"""

test15 = """
s = pyState.String(8)
x = 0
x += s.index('x')
"""

test16 = """
s = pyState.String(2)
x = "_"
x += "testt".rstrip(s)
"""

test17 = """
l1 = [1,2,3]
l2 = [4,5,6]
l1 += l2
"""

test18 = """
l1 = [1,2,3]
l1 *= 3
"""

test19 = """
s = "test"
s *= 3
"""

def test_pySym_AugAssign_MultString():
    b = ast_parse.parse(test19).body
    p = Path(b,source=test19)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()
    st = s.getVar('s')

    assert st.mustBe('test'*3)

def test_pySym_AugAssign_MultList():
    b = ast_parse.parse(test18).body
    p = Path(b,source=test18)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()
    l1 = s.getVar('l1')
    assert s.any_list(l1) == [1,2,3]*3

def test_pySym_AugAssign_AddLists():
    b = ast_parse.parse(test17).body
    p = Path(b,source=test17)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()
    l1 = s.getVar('l1')
    assert len(l1) == 6
    assert l1[0].mustBe(1)
    assert l1[1].mustBe(2)
    assert l1[2].mustBe(3)
    assert l1[3].mustBe(4)
    assert l1[4].mustBe(5)
    assert l1[5].mustBe(6)


def test_pySym_AugAssign_StateTracking():
    b = ast_parse.parse(test16).body
    p = Path(b,source=test16)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 5
   
    o = [p.state.any_str('x') for p in pg.completed] 
    o.sort()
    assert o == ['_te', '_te', '_tes', '_tes', '_testt']


def test_pySym_AugAssign_StateSplit():
    b = ast_parse.parse(test15).body
    p = Path(b,source=test15)
    pg = PathGroup(p)
    pg.explore()

    # There should be 10 possible states here
    assert len(pg.completed) == 8
    
    assert set([p.state.any_int('x') for p in pg.completed]) == set([x for x in range(8)])


def test_pySym_AugAssign_String_In_List():
    b = ast_parse.parse(test14).body
    p = Path(b,source=test14)
    pg = PathGroup(p)
    pg.explore()

    # There should be 10 possible states here
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_list('l') == ['a', 'bdE', 'c']


def test_pySym_AugAssign_MultipleStates():
    b = ast_parse.parse(test13).body
    p = Path(b,source=test13)
    pg = PathGroup(p)
    pg.explore()

    # There should be 10 possible states here
    assert len(pg.completed) == 10
    
    # Get the output states
    rets = []
    for p in pg.completed:
        rets.append(p.state.any_int('x'))
    
    assert set(rets) == set([1+x for x in range(10)])


def test_pySym_AugAssign_Subscript():
    b = ast_parse.parse(test9).body
    p = Path(b,source=test9)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,7.7,3]

    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1, 127, 3]

    b = ast_parse.parse(test11).body
    p = Path(b,source=test11)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1, 4, 3]

    b = ast_parse.parse(test12).body
    p = Path(b,source=test12)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1, 7, 3]


def test_pySym_AugAssign_Mod():
    b = ast_parse.parse(test8).body
    p = Path(b,source=test8)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert len(pg.deadended) == 0
    
    assert pg.completed[0].state.any_int('x') == 50%6
    assert pg.completed[0].state.any_int('y') == 50%6%4


def test_pySym_AugAssign_Pow():
    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert len(pg.deadended) == 0
    
    assert pg.completed[0].state.any_int('x') == 2 ** (2**4)


def test_pySym_AugAssign_SafeBitVec():
    # Ensuring that we notice over and underflows

    #######
    # Add #
    #######
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    pg.explore()
    
    assert len(pg.completed) == 0
    assert len(pg.deadended) == 1

    #######
    # Mul #
    #######
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 0
    assert len(pg.deadended) == 1

    #######
    # Sub #
    #######
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)
    pg.explore()
    
    assert len(pg.completed) == 0
    assert len(pg.deadended) == 1


def test_pySym_AugAssign_BitStuff():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('e') == 38776701190144


def test_pySym_AugAssign_MixedTypes():
    #######
    # Add #
    #######
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    ifSide,elseSide = p.step()
    elseSide = elseSide.step()[0]

    assert elseSide.state.isSat()
    assert elseSide.state.any_real('x') == 9.0
    assert elseSide.state.objectManager.getVar('x',ctx=elseSide.state.ctx).getZ3Object().is_real()



def test_pySym_AugAssign():
    #######
    # Add #
    #######
    b = ast_parse.parse(test1.format("+=")).body
    p = Path(b,source=test1.format("+="))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    ifSide,elseSide = p.step()
    elseSide = elseSide.step()[0]
    
    assert elseSide.state.isSat()
    assert elseSide.state.any_int('x') == 14

    ############
    # Subtract #
    ############
    b = ast_parse.parse(test1.format("-=")).body
    p = Path(b,source=test1.format("-="))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    ifSide,elseSide = p.step()
    elseSide = elseSide.step()[0]

    assert elseSide.state.isSat()
    assert elseSide.state.any_int('x') == 0

    ############
    # Multiply #
    ############
    b = ast_parse.parse(test1.format("*=")).body
    p = Path(b,source=test1.format("*="))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    ifSide,elseSide = p.step()
    elseSide = elseSide.step()[0]

    assert elseSide.state.isSat()
    assert elseSide.state.any_int('x') == 49

    ##########
    # Divide #
    ##########
    b = ast_parse.parse(test1.format("/=")).body
    p = Path(b,source=test1.format("/="))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    ifSide,elseSide = p.step()
    elseSide = elseSide.step()[0]

    assert elseSide.state.isSat()
    assert elseSide.state.any_int('x') == 1

    ##########
    # Modulo #
    ##########
    b = ast_parse.parse(test1.format("%=")).body
    p = Path(b,source=test1.format("%="))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    ifSide,elseSide = p.step()
    elseSide = elseSide.step()[0]

    assert elseSide.state.isSat()
    assert elseSide.state.any_int('x') == 0
