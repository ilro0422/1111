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
l = []
l.append(1)
l.append(2.3)
l.append([1,2.2,3])
"""

test2 = """
s = pyState.String(8)
l = []
l.append(s.index('a'))
"""

def test_function_List_append_statesplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8
    assert set([p.state.any_list('l').pop() for p in pg.completed]) == set(range(8))


def test_function_List_append():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [1, 2.3, [1, 2.2, 3]]

