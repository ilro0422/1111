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
from pySym.pyObjectManager.Real import Real
from pySym.pyObjectManager.List import List
from pySym.pyObjectManager.String import String
from pySym.pyObjectManager.Int import Int
from pySym.pyObjectManager.Char import Char
from pySym.pyObjectManager.BitVec import BitVec

import pytest

test1 = """
s = pyState.String(6)
c = pyState.String(1)[0]
r = pyState.Real()
bv = pyState.BVS(32)
l = [1,2,3]
l.insert(0, 0)
l.insert(0, 1.234)
l.insert(0,[1,2,4,5])
l.insert(0,"test")
l.insert(0,bv)
l.insert(0,s)
l.insert(0,c)
l.insert(0,r)

assert bv == 14
assert r == 5.15
assert c == "c"
assert ord(s[0]) == ord('s')
"""


def test_function_List_insert():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()

    # [5.15, 'c', 's\x00\x00\x00\x00\x00', 14, 'test', [1, 2, 4, 5], 1.234, 0, 1, 2, 3]
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()

    l = s.getVar('l')
    
    assert type(l[0]) == Real
    assert type(l[1]) == String and len(l[1]) == 1
    assert type(l[2]) == String
    assert type(l[3]) == BitVec
    my_list = s.any_list(l)
    assert my_list[0] == 5.15
    assert my_list[1] == "c"
    assert my_list[2].startswith("s")
    assert my_list[3] == 14
    assert my_list[4] == "test"
    assert my_list[5] == [1,2,4,5]
    assert my_list[6] == 1.234
    assert my_list[7:] == [0,1,2,3]

