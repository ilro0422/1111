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
s = "abcd"
l = [x for x in s] + [1,2]
x = len(s)
y = len(l)
"""

test2 = """
s = pyState.String(8)
x = len("A" * s.index('a'))
"""

def test_fnuction_len_statesplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    assert set([p.state.any_int('x') for p in pg.completed]) == set(range(8))


def test_function_len():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_int('x') == 4
    assert pg.completed[0].state.any_int('y') == 6

