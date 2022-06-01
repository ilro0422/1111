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
x = "test ".rstrip()
y = "test".rstrip()
z = "test".rstrip("t")
d = "test".rstrip("st")
"""

test2 = """
s = pyState.String(8)
x = "test1".rstrip(str(s.index('a')))
"""

test3 = """
s = pyState.String(2)
x = "testt"
x = x.rstrip(s)
"""

test4 = """
s = pyState.String(8)
x = s.rstrip("x")
"""

test5 = """
s = "mee"
s2 = pyState.String(1)
x = ''.join([x for x in s.rstrip(s2)])
"""

test6 = """
x = "test".rstrip(pyState.String(1) + "t")
"""

def test_function_String_rstrip_partiallySymbolic():
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 3
    o = [p.state.any_str('x') for p in pg.completed]
    o.sort()
    assert o == ['te', 'tes', 'tes']


def test_function_String_rstrip_Char():
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 2
    assert set([p.state.any_str('x') for p in pg.completed]) == {"m","mee"}


def test_function_String_rstrip_symbolicStrip():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 5
    o = [p.state.any_str('x') for p in pg.completed]
    o.sort()
    # 3 cases. 1) both chars miss, 2) one char hit's "t" and the other misses. 3) one hits
    # "t" and the other hits "s"
    assert o == ['te', 'te', 'tes', 'tes', 'testt']

    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 9

    # TODO: This is a brittle match..
    o = [p.state.any_str('s') for p in pg.completed]
    # Sort by number of 'x' that appear in the output
    o = sorted(o, key=lambda x: x.count('x'))
    assert not o[0].endswith("x")
    for x in range(1,8):
        assert o[x].endswith("x"*x)
    #['\x00\x00\x00\x00\x00\x00\x00\x00', '\x00\x00\x00\x00\x00\x00\x00x', '\x00\x00\x00\x00\x00\x00xx', '\x00\x00\x00\x00\x00xxx', '\x00\x00\x00\x00xxxx', '\x00\x00\x00xxxxx', '\x00\x00xxxxxx', '\x00xxxxxxx', 'xxxxxxxx']



def test_function_String_rstrip_statesplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    o = [p.state.any_str('x') for p in pg.completed]
    o.sort()
    assert o == ['test', 'test1', 'test1', 'test1', 'test1', 'test1', 'test1', 'test1']


def test_function_String_rstrip():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_str('x') == "test ".rstrip()
    assert pg.completed[0].state.any_str('y') == "test".rstrip()
    assert pg.completed[0].state.any_str('z') == "test".rstrip("t")
    assert pg.completed[0].state.any_str('d') == "test".rstrip("st")

