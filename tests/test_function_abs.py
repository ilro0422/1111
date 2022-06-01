import sys, os
#myPath = os.path.dirname(os.path.abspath(__file__))
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
x = 10
y = -10
z = pyState.Int()
a = abs(x)
b = abs(y)
c = abs(10)
d = abs(-10)
e = abs(z)
"""

def test_funcion_abs():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('a') == 10
    assert pg.completed[0].state.any_int('b') == 10
    assert pg.completed[0].state.any_int('c') == 10
    assert pg.completed[0].state.any_int('d') == 10




