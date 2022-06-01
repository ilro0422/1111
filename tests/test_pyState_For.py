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
out = 0
for x in [1,2,3,4,5]:
    out += x
"""

test2 = """
out = 0
for x in [1,2,3,4,5]:
    for y in [10,11,12,13]:
        out += x + y
"""

test3 = """
out = 0
q = [1,2,3,4,5]
for x in q:
    for y in [10,11,12,13]:
        out += x + y
"""

test4 = """
out = 0
q = [1,2,3,4,5]
for x in q[:2]:
    for y in [10,11,12,13]:
        out += x + y

    if x == 3:
        break
"""

test5 = """
a = 0
b = 0
for x in zip([1,8],[2,3]):
    a += x[0]
    b += x[1]
"""

def test_pySym_For_ListReturn():
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_int('a') == 9 
    assert pg.completed[0].state.any_int('b') == 5


def test_pySym_variableSlice():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('out') == 104


def test_pySym_variableFor():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('out') == 290
    assert pg.completed[0].state.any_list('q') == [1,2,3,4,5]


def test_pySym_nestedFor():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('out') == 290


def test_pySym_stupidFor():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('out') == 15
    assert pg.completed[0].state.any_int('x') == 5


