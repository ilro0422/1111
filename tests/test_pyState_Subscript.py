import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

import logging
from pySym import Colorer
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
from pySym.pyPathGroup import PathGroup
import pytest

test1 = """
l = [1,2,3]
x = l[1]
"""

test2 = """
i = 2
l = [1,2,3]
x = l[i]
"""

test3 = """
def test():
    return 4

l = [1,2,3,[test(),5]]
x = l[3][0]
"""

test4 = """
def test():
    return 4

l = [1,2,3,[test(),5]]
x = l[3]
"""

test5 = """
l = [1,2,3,[4,[5,6,7]]]
x = l[3][1]
"""

test6 = """
i = pyState.BVV(123,64)
l = [1,2.2,3.1415,4,i]
x = l[::2]
"""

test7 = """
i = pyState.BVV(123,64)
l = [1,2.2,3.1415,4,i]
x = l[::-1]
"""

test8 = """
i = pyState.BVV(123,64)
l = [1,2.2,3.1415,4,i,8,[1,2,3]]
x = l[:]
"""

test9 = """
i = pyState.BVV(123,64)
l = [1,2.2,3.1415,4,i,8,[1,2,3]]
x = l[::-1]
"""

test10 = """
i = pyState.BVV(123,64)
l = [1,2.2,3.1415,4,i,8,[1,2,3]]
x = l[1:7:2]
"""

test11 = """
l = [1,[2,3],4]
x = l[0:2][1][1]
"""

test12 = """
l = [1,2.2,3,4,5]
i = pyState.Int()
x = l[i]
"""

test13 = """
l = [1,2,3,4,5]
i = pyState.Int()
x = l[i]
"""

test14 = """
l = [1,2,3,4]
x = l[-1:]
y = l[-3:-1]

s = "test"
a = s[-1:]
b = s[-3:-1]
"""

def test_pyState_Subscript_negative_slices():
    b = ast_parse.parse(test14).body
    p = Path(b,source=test14)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    
    s = pg.completed[0].state.copy()

    a = s.getVar('a')
    b = s.getVar('b')
    x = s.getVar('x')
    y = s.getVar('y')

    assert a.mustBe("test"[-1:])
    assert b.mustBe("test"[-3:-1])
    
    assert len(x) == 1
    assert x[0].mustBe(4)

    assert len(y) == 2
    assert y[0].mustBe(2)
    assert y[1].mustBe(3)

def test_pyState_Subscript_symbolic_index():
    b = ast_parse.parse(test12).body
    p = Path(b,source=test12)
    pg = PathGroup(p)
    
    pg.explore()
    
    # Should split into 5 paths
    assert len(pg.completed) == 5
    
    assert sorted([p.state.getVar('x').getValue() for p in pg.completed]) == [1,2.2,3,4,5]

    b = ast_parse.parse(test13).body
    p = Path(b,source=test13)
    pg = PathGroup(p)
    
    pg.explore()
    
    # This should only have 1 path through
    assert len(pg.completed) == 1


def test_pyState_nestedSlice():
    b = ast_parse.parse(test11).body
    p = Path(b,source=test11)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 3


def test_pyState_SubscriptSlice():
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [1, 3.1415, 123]

    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [123, 4, 3.1415, 2.2, 1]

    b = ast_parse.parse(test8).body
    p = Path(b,source=test8)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [1,2.2,3.1415,4,123,8,[1,2,3]]

    b = ast_parse.parse(test9).body
    p = Path(b,source=test9)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [1,2.2,3.1415,4,123,8,[1,2,3]][::-1]

    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [2.2, 4, 8]



def test_pyState_AssignListFromSubscript():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [4,5]

    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('x') == [5,6,7]



def test_pyState_Subscript_MultiDimentional():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 4


def test_pyState_Subscript_VariableSubscript():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 3


def test_pyState_Subscript_AssignToVar():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 2

