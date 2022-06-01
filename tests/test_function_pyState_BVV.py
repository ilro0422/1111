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
from pySym.pyState.z3Helpers import Z3_MAX_STRING_LENGTH

test1 = """
x = pyState.BVV((16 >> 4)&1,1) # Results in BitVec 1 of size 1
y = pyState.BVV((16 >> 4)&1,2**10) # Results in BitVec 1 of size 1024
"""

def test_function_pyState_BVV_basic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    x = pg.completed[0].state.getVar('x')
    y = pg.completed[0].state.getVar('y')

    assert x.isStatic() and x.mustBe(1) and x.size == 1
    assert y.isStatic() and y.mustBe(1) and y.size == 1024
