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
x = "test"
y = x.zfill(5)
z = x.zfill(3)
d = x.zfill(10)
"""

test2 = """
s = pyState.String(8)
x = "test"
y = x.zfill(s.index('a'))
"""

def test_function_String_zfill_statesplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()

    # Every index should be a possibility
    assert len(pg.completed) == 8

    o = [p.state.any_str('y') for p in pg.completed]
    o.sort()
    assert o == ['000test', '00test', '0test', 'test', 'test', 'test', 'test', 'test']


def test_function_String_zfill_static():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()

    # Every index should be a possibility
    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_str('x') == "test"
    assert pg.completed[0].state.any_str('y') == "0test"
    assert pg.completed[0].state.any_str('z') == "test"
    assert pg.completed[0].state.any_str('d') == "000000test"

