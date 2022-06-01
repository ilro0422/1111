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
s = "Test"
"""

test2 = """
s = "Test"
l = [x for x in s]
"""

test3 = """
s = "abcd"
d = "abcd"
f = "Abcd"
g = pyState.String(4)
"""

test4 = """
s = "abcd"
d = pyState.String(5)
"""

def test_pyObjectManager_String_isStatic():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    s = pg.completed[0].state.getVar('s')
    d = pg.completed[0].state.getVar('d')

    assert s.isStatic()
    assert s.getValue() == "abcd"
    
    assert not d.isStatic()


def test_pyObjectManager_String_canBe_mustBe_String():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.getVar('s')
    d = pg.completed[0].state.getVar('d')
    f = pg.completed[0].state.getVar('f')
    g = pg.completed[0].state.getVar('g')

    assert s.canBe(d)
    assert not s.canBe(f)
    assert g.canBe(s)
    assert not g.mustBe(s)
    assert g.canBe(f)


def test_pyObjectMAnager_String_mustBe():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.getVar('s')

    assert s.mustBe("Test")
    assert not s.mustBe("test")


def test_pyObjectManager_String_canBe():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.getVar('s')
    
    assert s.canBe("Test")
    assert not s.canBe("test")
    assert s[0:1].canBe("T")
    assert not s[0:2].canBe("T3")
    assert s[:3].canBe("Tes")


def test_pyObjectManager_String_ListComp():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_list('l') == [x for x in "Test"]


def test_pyObjectManager_String_Assign():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_str('s') == "Test"


