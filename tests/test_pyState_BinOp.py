import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
import pytest
from pySym.pyPathGroup import PathGroup

test1 = """
x = 1.5 
y = 2.5
x = x {0} y
"""

test2 = """
x = 7
y = 5
x = x % y
"""

test3 = """
x = 2
x = x + 3.5
"""

test4 = """
a = 10
b = 1
c = 6
d = a ^ b ^ c
"""

test5 = """
a = 0x10325476
b = 0x98BADCFE
c = 0xEFCDAB89
d = 0x67452301
g = 0x12345678
e = (d ^ ((b & (c ^ a)) & g >> 2)) << 15
"""

test6 = """
h = pyState.BVV(1337,64)
h = h + 0xffffffffffffffff
"""

test7 = """
h = pyState.BVV(1337,64)
h = h * 0xffffffffffffff
"""

test8 = """
h = pyState.BVV(1337,64)
h = h - 1338
"""

test9 = """
def test(x,y):
    return x**y

x = test(2,4)**8
"""

test10 = """
s = "test" + " blerg"
s2 = pyState.String(8) + " blerg"
s3 = "This " + "is " + "a " + "test"
"""

test11 = """
l = [1,2,3] + [4,5,6]
"""

test12 = """
l = [1,2,3] * 3
p = 3 * [1,2,3]
"""

test13 = """
s = pyState.String(8)
x = 1 + s.index('x')
"""

test14 = """
x = "A" * 4
"""

test15 = """
s = pyState.String(8)
x = s.rstrip("x") * 2
"""

def test_pySym_BinOp_StatePropagation():
    b = ast_parse.parse(test15).body
    p = Path(b,source=test15)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 9

    # Check that the x value (output) is correct
    assert set([len(p.state.any_str('x')) for p in pg.completed]) == set([x*2 for x in range(9)])

    # Check that the back-propogation of the s values are also accurate
    assert set([len(p.state.any_str('s')) - len(p.state.any_str('s').rstrip("x")) for p in pg.completed]) == set(range(9))


def test_pySym_BinOp_StringMult():
    b = ast_parse.parse(test14).body
    p = Path(b,source=test14)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_str('x') == "A" * 4


def test_pySym_BinOp_StateSplit():
    b = ast_parse.parse(test13).body
    p = Path(b,source=test13)
    pg = PathGroup(p)
    pg.explore()

    # There should be 8 states now
    assert len(pg.completed) == 8
    assert set([p.state.any_int('x') for p in pg.completed]) == set([x for x in range(1,9)])


def test_pySym_BinOp_ListMult():
    b = ast_parse.parse(test12).body
    p = Path(b,source=test12)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,3] * 3
    assert pg.completed[0].state.any_list('l') == 3 * [1,2,3]


def test_pySym_BinOp_ListConcat():
    b = ast_parse.parse(test11).body
    p = Path(b,source=test11)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,3] + [4,5,6]


def test_pySym_BinOp_StrConcat():
    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_str('s') == "test" + " blerg"
    
    assert len(pg.completed[0].state.any_str('s2')) == 8 + len(" blerg")
    assert pg.completed[0].state.any_str('s2').endswith(" blerg")

    assert pg.completed[0].state.any_str('s3') == "This " + "is " + "a " + "test"


def test_pySym_BinOp_Exp():
    b = ast_parse.parse(test9).body
    p = Path(b,source=test9)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1
    assert len(pg.deadended) == 0

    assert pg.completed[0].state.any_int('x') == (2**4)**8

def test_pySym_BinOp_SafeBitVec():
    # Ensuring that we notice over and underflows

    #######
    # Add #
    #######
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)
    pg.explore()
    
    assert len(pg.completed) == 0
    assert len(pg.deadended) == 1

    #######
    # Mul #
    #######
    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 0
    assert len(pg.deadended) == 1

    #######
    # Sub #
    #######
    b = ast_parse.parse(test8).body
    p = Path(b,source=test8)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 0
    assert len(pg.deadended) == 1




def test_pySym_BinOp_BitStuff():
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)
    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('e') == 57065549561856


def test_pySym_BinOp_Xor():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('d') == 13


def test_pySym_BinOp():
    #######
    # Add #
    #######
    b = ast_parse.parse(test1.format("+")).body
    p = Path(b,source=test1.format("+"))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    p = p.step()[0]
    
    assert p.state.isSat()
    assert p.state.any_real('x') == 4.0

    #######
    # Sub #
    #######
    b = ast_parse.parse(test1.format("-")).body
    p = Path(b,source=test1.format("-"))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    p = p.step()[0]

    assert p.state.isSat()
    assert p.state.any_real('x') == -1.0

    #######
    # Mul #
    #######
    b = ast_parse.parse(test1.format("*")).body
    p = Path(b,source=test1.format("*"))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    p = p.step()[0]

    assert p.state.isSat()
    assert p.state.any_real('x') == 3.75

    #######
    # Div #
    #######
    b = ast_parse.parse(test1.format("/")).body
    p = Path(b,source=test1.format("/"))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    p = p.step()[0]

    assert p.state.isSat()
    assert p.state.any_real('x') == 0.6

    #######
    # Mod #
    #######
    b = ast_parse.parse(test2.format("%")).body
    p = Path(b,source=test2.format("%"))
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    p = p.step()[0]

    assert p.state.isSat()
    assert p.state.any_int('x') == 2

def test_mixedTypes():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    print(p.state.solver)
    print(p.state.isSat())
    assert p.state.isSat()
    assert p.state.any_real('x') == 5.5

