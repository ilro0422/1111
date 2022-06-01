import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))

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
import pySym

test1 = """
x = ord("A")
s = "Test"
y = ord(s[0])
"""

test2 = """
s = pyState.String(8)
x = ord(str(s.index('a')))
"""

def test_function_ord_symbolic_input():
    proj = pySym.Project(os.path.join(myPath, "scripts", "ord_symbolic_chr.py"))
    pg = proj.factory.path_group()
    pg.explore()

    assert len(pg.completed) == 1

    s = pg.completed[0].state.getVar('s')
    c = pg.completed[0].state.getVar('c')

    # Set the integer value, back prop to the string
    c.setTo(ord('X'))
    assert str(s)[1] == "X"


def test_function_ord_StateSplitting():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    assert set([p.state.any_int('x') for p in pg.completed]) == set([ord(str(x)) for x in range(8)])
    


def test_function_ord():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert chr(pg.completed[0].state.any_int('x')) == "A"
    assert chr(pg.completed[0].state.any_int('y')) == "T"


