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
from pySym.pyState.z3Helpers import Z3_MAX_STRING_LENGTH

test1 = """
s = pyState.String(32)
s2 = pyState.String()
"""


def test_function_pyState_String():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    s = pg.completed[0].state.getVar('s')
    s2 = pg.completed[0].state.getVar('s2')

    assert len(s) == 32
    assert len(s2) == Z3_MAX_STRING_LENGTH
    
