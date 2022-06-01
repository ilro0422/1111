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
x = s.index("{0}")
"""

test2 = """
s = pyState.String(10)
x = s.index('a')
"""

test3 = """
s = pyState.String(10)
x = -1
if s[3] == "a":
    x = s.index('a')
"""



def test_function_String_Index_PartiallySymbolic():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()

    # Every index should be a possibility
    assert len(pg.completed) == 5

    indexes = []
    # Make sure we got all of them
    for path in pg.completed:
        indexes.append(path.state.any_int('x'))

    assert set(indexes) == set(range(4)).union({-1})



def test_function_String_Index_Symbolic():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()

    # Every index should be a possibility
    assert len(pg.completed) == 10
    
    indexes = []
    # Make sure we got all of them
    for path in pg.completed:
        indexes.append(path.state.any_int('x'))
    
    assert set(indexes) == set(range(10))


def test_function_String_Index():
    b = ast_parse.parse(test1.format("T")).body
    p = Path(b,source=test1.format("T"))
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_int('x') == 0

    b = ast_parse.parse(test1.format("t")).body
    p = Path(b,source=test1.format("t"))
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_int('x') == 3

    b = ast_parse.parse(test1.format("es")).body
    p = Path(b,source=test1.format("es"))
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_int('x') == 1

    b = ast_parse.parse(test1.format("st")).body
    p = Path(b,source=test1.format("st"))
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_int('x') == 2



