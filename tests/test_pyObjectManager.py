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
l = [1,2.2,3]
q = [1,2,[3,4]]
"""

test2 = """
l = [1,2,3]
s = "test"
i = 1337
bvs = pyState.BVS(32)
"""

def test_pyObjectManager_uuid():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    l = s.getVar('l')
    for elm in l:
        assert type(elm.uuid) is bytes
    assert type(l.uuid) is bytes

    st = s.getVar('s')
    assert type(st.uuid) is bytes
    for elm in st:
        assert type(elm.uuid) is bytes
    
    i = s.getVar('i')
    assert type(i.uuid) is bytes

    bvs = s.getVar('bvs')
    assert type(bvs.uuid) is bytes


def test_pyObjectManager_getParent():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    l = pg.completed[0].state.getVar('l')
    i = l[2]
    
    # Make sure it returned the right object
    assert pg.completed[0].state.objectManager.getParent(i) == l

    q = pg.completed[0].state.getVar('q')
    i = q[2][0]
    
    # Check that it recurses fully
    assert pg.completed[0].state.objectManager.getParent(i) == q[2]


