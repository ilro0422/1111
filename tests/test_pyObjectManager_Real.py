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
x = 1.5
"""

test2 = """
x = pyState.Real()
y = 5.5
z = 2
"""

test3 = """
x = 6.2
"""



def test_pyObjectManager_Real_strPrint():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    assert x.__str__() == "6.2"


def test_pyObjectManager_Real_setTo():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    y = pg.completed[0].state.getVar('y')
    z = pg.completed[0].state.getVar('z')

    x.setTo(1337.4)
    assert pg.completed[0].state.any_real('x') == 1337.4
    x.increment()
    x.setTo(y)
    assert pg.completed[0].state.any_real('x') == 5.5
    
    x.increment()
    x.setTo(z)
    assert pg.completed[0].state.any_real('z') == 2



def test_pyObjectManager_Real_isStatic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    x = pg.completed[0].state.getVar('x')
    
    assert x.isStatic()
    assert x.getValue() == 1.5


