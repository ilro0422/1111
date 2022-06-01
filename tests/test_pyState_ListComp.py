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
l = [x for x in range(5)]
"""

test2 = """
l = [x for x in [1,2,3,4,5] if x%2 == 0]
"""

test3 = """
l = [x for x in range(10) if x%2 == 0 or x%3 == 0]
"""

test4 = """
l = [x for x in [1,2,3,4,5] for y in [1,2,3]]
"""

test5 = """
l = [[x,y] for x in [1,2,3] for y in [1]]
"""

test6 = """
l = [x**2 for x in range(5)]
"""

test7 = """
s = "abcd"
l = [x for x in s if x == "b"]
"""

test8 = """
l = [str(i) for i in range(10)]
"""

def test_pyState_ListComp_MoreFunctions():
    b = ast_parse.parse(test8).body
    p = Path(b,source=test8)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [str(i) for i in range(10)]


def test_pyState_ListComp_StringCmp():
    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == ["b"]


def test_pyState_ListComp_outputModifier():
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [x**2 for x in range(5)]


def test_pyState_ListComp_MultipleFor_ReturnList():
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [[x,y] for x in [1,2,3] for y in [1]]


def test_pyState_ListComp_MultipleFor():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [x for x in [1,2,3,4,5] for y in [1,2,3]]
    
    with pytest.raises(Exception):
        pg.completed[0].state.any_int('x')


def test_pyState_ListComp_BoolComp():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [x for x in range(10) if x%2 == 0 or x%3 == 0]


def test_pyState_ListComp_If():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [x for x in [1,2,3,4,5] if x%2 == 0]


def test_pyState_ListComp_Simple():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == [x for x in range(5)]

