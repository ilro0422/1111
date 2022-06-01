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
s1 = pyState.BVS(1)
s2 = pyState.BVS(1)
"""

test2 = """
l = []

for i in range(24):
    l.append(pyState.BVS(1))
"""

def test_function_pyState_BVS_ret_as_list():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

def test_function_pyState_BVS_basic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    s1 = pg.completed[0].state.getVar('s1')
    s2 = pg.completed[0].state.getVar('s2')

    # Make sure that we're not duplicating variables on creation
    assert str(s1.getZ3Object()) != str(s2.getZ3Object())
