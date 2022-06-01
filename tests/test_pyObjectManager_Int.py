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
x = 1
"""

test2 = """
x = pyState.Int()
y = 5
"""

test3 = """
x = 12
"""

test4 = """
l = [pyState.Int(), pyState.Int()]
if l[0] != l[1]:
    pass
if l[0] == l[1]:
    pass

pass
"""

test5 = """
i = pyState.Int()
l = [0,1,2,3,4,5]
x = l[i]
"""

def test_pyObjectManager_Int_is_unconstrained():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    x = s.getVar('x')

    assert x.is_unconstrained
    
    # add a real constraint
    s.addConstraint(x.getZ3Object() > 5)
    assert x.is_constrained


def test_pyObjectManager_Int_PostSet():
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1

    for q in range(6):
        s = pg.completed[0].state.copy()
        x = s.getVar('x')
        i = s.getVar('i')
        i.setTo(q)
        assert x.getValue() == q
    


def test_pyObjectManager_Int_MultipleObj():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore(find=4)
    assert len(pg.found) == 1

    pg = PathGroup(p)
    pg.explore(find=6)

    assert len(pg.found) == 1

def test_pyObjectManager_Int_strPrint():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    assert x.__str__() == "12"

def test_pyObjectManager_Int_setTo():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    y = pg.completed[0].state.getVar('y')
    x.setTo(1337)

    assert pg.completed[0].state.any_int('x') == 1337
    x.increment()
    x.setTo(y)

    #assert pg.completed[0].state.any_int('x') == 5
    assert x.getValue() == 5


def test_pyObjectManager_Int_isStatic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    
    assert x.isStatic()
    assert x.getValue() == 1


