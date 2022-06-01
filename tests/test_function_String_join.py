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
x = ''.join(["1","2","3"])
y = ','.join(["4","5","6"])
z = "".join([str(i) for i in [1,2,3]])
"""

test2 = """
s = pyState.String(8)
x = "".join([str(x) for x in range(s.index('a'))])
"""

def test_function_strJoin_statesplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    out = [p.state.any_str('x') for p in pg.completed]
    out.sort()
    assert out == ['', '0', '01', '012', '0123', '01234', '012345', '0123456']


def test_function_strJoin():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_str('x') == ''.join(["1","2","3"])
    assert pg.completed[0].state.any_str('y') == ','.join(["4","5","6"])
    assert pg.completed[0].state.any_str('z') == "".join([str(i) for i in [1,2,3]])
