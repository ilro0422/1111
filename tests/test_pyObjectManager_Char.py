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
from pySym.pyObjectManager.Char import Char

test1 = """
s = "Test"
d = pyState.String(10)
"""

test2 = """
s = "Blerg"
c2 = pyState.String(1)
"""

test3 = """
c = "b"
"""

test4 = """
s = pyState.String(1)
d = "Test"
e = "Feet"
"""

def test_pyObjectManager_Char_is_unconstrained():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    c = s.getVar('s')[0]

    assert c.is_unconstrained
    
    # For now, this will add bounded int constraints to the solver...
    z3_obj = c.getZ3Object()
    # Those bounds should not count as constrained
    assert c.is_unconstrained

    # This constraint should eval to True, and not be added
    s.addConstraint(z3_obj > 5)
    assert c.is_unconstrained

    # Try with symbolic
    c = s.getVar('c2')[0]
    
    assert c.is_unconstrained
    
    # For now, this will add bounded int constraints to the solver...
    z3_obj = c.getZ3Object()
    # Those bounds should not count as constrained
    assert c.is_unconstrained

    # This should add a real constraint
    s.addConstraint(z3_obj > 5)
    assert c.is_constrained

def test_pyObjectManager_Char_mustBe():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.getVar('s')
    d = pg.completed[0].state.getVar('d')
    e = pg.completed[0].state.getVar('e')
    
    assert s[0].canBe(d[0])
    assert s[0].canBe("b")
    assert not s[0].mustBe("b")
    assert not s[0].mustBe(d[0])
    assert not s[0].canBe("test")

    assert d[1].canBe(e[1])
    assert d[1].mustBe(e[2])


def test_pyObjectManager_Char_strPrint():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    c = pg.completed[0].state.getVar('c')
    c = c[0]
    
    assert c.__str__() == "b"
    

def test_pyObjectManager_Char_setTo():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    c = pg.completed[0].state.getVar('c',varType=Char)

    c.setTo('x')
    assert c.getValue() == "x"


def test_pyObjectManager_Char_isStatic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    s = pg.completed[0].state.getVar('s')
    d = pg.completed[0].state.getVar('d')

    assert s[0].isStatic()
    assert s[0].getValue() == "T"
    
    assert not d.isStatic()

