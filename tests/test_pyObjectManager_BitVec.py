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
x = pyState.BVV(5,16)
"""

test2 = """
x = pyState.BVS(32)
y = pyState.BVV(15,32)
"""

test3 = """
x = pyState.BVV(1234,32)
"""

test4 = """
x = pyState.BVS(32)
assert x == 1234
"""

def test_pyObjectManager_BitVec_as_int():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    x = s.getVar('x')
    assert int(x) == 1234


def test_pyObjectManager_BitVec_is_unconstrained():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    x = s.getVar('x')

    assert x.is_unconstrained
    
    # add a real constraint
    s.addConstraint(x.getZ3Object() > 14)
    assert x.is_constrained


def test_pyObjectManager_BitVec_strPrint():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    assert x.__str__() == "1234"


def test_pyObjectManager_BitVec_setTo():
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
    assert pg.completed[0].state.any_int('x') == 15
    


def test_pyObjectManager_BitVec_isStatic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    
    assert x.isStatic()
    assert x.getValue() == 5


