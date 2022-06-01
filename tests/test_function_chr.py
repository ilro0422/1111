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
import pySym

test1 = """
i = 88 # 'X'
c = chr(i)
"""

test2 = """
i = pyState.Int()
c = chr(i)
"""

def test_function_chr_symbolic_input():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.completed) == 1

    i = pg.completed[0].state.getVar('i')
    c = pg.completed[0].state.getVar('c')

    # Set i, check that it propagates to c.
    i.setTo(ord('X'))
    assert str(c) == "X"

def test_function_chr():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert chr(pg.completed[0].state.any_int('c')) == 'X'
