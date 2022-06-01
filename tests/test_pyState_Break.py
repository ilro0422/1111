import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
import pytest
from pySym.pyPathGroup import PathGroup

test1 = """
x = 0
y = 1
while x < 10:
    if x == 5:
        if y == 1:
            break
    x += 1

y = 1
"""

test2 = """
out = 0
q = [1,2,3,4,5]
for x in q:
    for y in [10,11,12,13]:
        out += x + y

    if x == 3:
        break
"""

def test_pySym_breakFor():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('out') == 162
    assert pg.completed[0].state.any_int('x') == 3


def test_pySym_breakWhile():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 5


