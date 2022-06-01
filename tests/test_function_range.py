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
for i in range(0,10,2):
    for j in range(5):
        out += i + j
"""

test2 = """
out = 0
l = range(4,10)
"""

test3 = """
out = 0
l = range(12)
"""

test4 = """
s = pyState.String(8)
x = range(s.index('a'))
"""

def test_function_range_StateSplit():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    out = [p.state.any_list('x') for p in pg.completed]
    out.sort()
    assert out == [[], [0], [0, 1], [0, 1, 2], [0, 1, 2, 3], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5, 6]]


def test_function_range():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('out') == 150

    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [4, 5, 6, 7, 8, 9]

    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

