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
s = 5
x = bin(12)
y = bin(13)[2:]
z = bin(s)
"""

test2 = """
s = pyState.String(8)
x = bin(s.index('a'))
"""

def test_funcion_bin_StateSplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    
    # We should get 8 states back
    assert len(pg.completed) == 8
    assert set([int(p.state.any_str('x'),2) for p in pg.completed]) == set(range(8))


def test_function_bin():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_str('x') == bin(12)
    assert pg.completed[0].state.any_str('y') == bin(13)[2:]
    assert pg.completed[0].state.any_str('z') == bin(5)

