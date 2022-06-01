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

test1 = """
x = -1
y = -x
z = +x
"""

def test_pySym_UnaryOp_Simple():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == -1
    assert pg.completed[0].state.any_int('y') == 1
    assert pg.completed[0].state.any_int('z') == -1

