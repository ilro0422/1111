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
from pySym.pyObjectManager.Int import Int
from pySym.pyObjectManager.Real import Real
from pySym.pyObjectManager.BitVec import BitVec
from pySym.pyObjectManager.List import List

test1 = """
l = [1,2.2,3]
"""

test2 = """
l = [1,2.2,[3,[4,5],6]]
"""

test3 = """
x = 3
l = [1,2,x,4]
"""

test4 = """
x = 3
l = [1,2,[x,4]]
"""

test5 = """
x = 3
l = [1,2,[x,4]]
x = 5
"""

test6 = """
y = 1
x = y+3
l = [1,2,x,4]
"""

test7 = """
l = [1,2,3,4]
l = [4,3,2,1]
"""

test8 = """
x = pyState.BVV(1337,32)
l = [1,2,x,4]
"""

test9 = """
x = pyState.BVV(1337,32)
l = [1,[2,x],4]
"""

test10 = """
def test():
    return 12

l = [1,test(),[test() + test()]]
"""

test11 = """
l = [1,2,3]
k = [1,2,3]
j = [2,2,3]
"""

test12 = """
s = pyState.String(8)
l = ["test",s.index('a')]
"""

test13 = """
l1 = [1,2,3]
l2 = [4,5,6]
"""

def test_pyObjectManager_List_addList():
    b = ast_parse.parse(test13).body
    p = Path(b,source=test13)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    s = pg.completed[0].state.copy()
    l1 = s.getVar('l1')
    l2 = s.getVar('l2')
    l3 = l1 + l2

    # Because I don't have List.mustBe working rn
    assert l3[0].mustBe(1)
    assert l3[1].mustBe(2)
    assert l3[2].mustBe(3)
    assert l3[3].mustBe(4)
    assert l3[4].mustBe(5)
    assert l3[5].mustBe(6)


def test_pyObjectManager_List_StateSplit():
    b = ast_parse.parse(test12).body
    p = Path(b,source=test12)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    assert set([p.state.any_list('l')[1] for p in pg.completed]) == set(range(8))


def test_pyObjectManager_List_canBe():
    b = ast_parse.parse(test11).body
    p = Path(b,source=test11)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    l = pg.completed[0].state.getVar('l')
    k = pg.completed[0].state.getVar('k')
    j = pg.completed[0].state.getVar('j')
    
    assert l.canBe(k)
    assert not l.canBe(j)

    assert l.mustBe(k)


def test_pyObjectManager_List_setitem():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    l = pg.completed[0].state.getVar('l')

    s = pg.completed[0].state

    # Base check
    assert l[1].count == 0
    assert type(l[1]) == Real

    # Assign an Int
    l[1] = Int(varName='x',ctx=0,state=s)
    assert l[1].count == 1
    assert type(l[1]) == Int

    # Assign back to Real
    l[1] = Real(varName='x',ctx=0,state=s)
    assert l[1].count == 2
    assert type(l[1]) == Real
    
    # Assign to BitVec
    l[1] = BitVec(varName='x',ctx=0,size=32,state=s)
    assert l[1].count == 3
    assert type(l[1]) == BitVec
    
    # Assign List
    l[1] = List(varName='x',ctx=0,state=s)
    #assert l[1].count == 4
    assert type(l[1]) == List


def test_pyObjectManager_List_FunctionCalls():
    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1, 12, [24]]


def test_pyObjectManager_List_BitVec():
    b = ast_parse.parse(test8).body
    p = Path(b,source=test8)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,1337,4]

    b = ast_parse.parse(test9).body
    p = Path(b,source=test9)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,[2,1337],4]



def test_pyObjectManager_List_ReAssign():
    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [4,3,2,1]


def test_pyObjectManager_List_varInList():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,3,4]

    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,[3,4]]


    # NOTE: This is correct behavior. Python resolves the object when creating the list
    # Updating the var later has no affect on the list
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,[3,4]]

    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2,4,4]



def test_pyObjectManager_List_BasicAssign():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2.2,3]

def test_pyObjectManager_List_NestedList():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1,2.2,[3,[4,5],6]]

