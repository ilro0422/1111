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
from copy import copy


test1 = """
x = 0
while x < 10:
    x += 1

y = 1
"""

test2 = """
def test():
    return 5

x = 0
while x < test():
    x += 1

y = 1
"""

test3 = """
def test(x,y):
    return x + y

x = 0
z = 0
while x < 5:
    y = 0
    while y < 3:
        z = z + test(x,y)
        y += 1
    x += 1

z = z
"""

test4 = """
def test(x,y):
    return x + y

x = 0
z = 0
while x < 5:
    y = 0
    while y < 3:
        z += test(x,y)
        y += 1
    x += 1

z = z
"""

test5 = """
def test(x,y):
    out = 2
    while x < y:
        out *= x
        x += 1
    
    return out

x = 0
z = 0
while x < 5:
    y = 0
    while y < 3:
        z += test(x,y)
        y += 1
    x += 1

z = z
"""

test6 = """
x = 0
y = 0
o = 0
while x < 10:
    while y < 5:
        o += 1
        y += 1
    x += 1

print(o)
"""

test7 = """
s = pyState.String(3)
x = 0
while x < s.index('a'):
    x += 1
"""


def test_pySym_While_StateSplit():
    # TODO: I'm not 100% sure this is right.. But can't think of why it's wrong atm...
    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) > 0

    assert set([p.state.any_int('x') for p in pg.completed]) == set([0,1,2])


def test_pySym_stupidWhile():
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)
    
    pg.explore()
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 10
    assert pg.completed[0].state.any_int('y') == 5
    assert pg.completed[0].state.any_int('o') == 5


def test_pySym_complicated():
    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)
    
    assert pg.explore(find=19)
    assert pg.found[0].state.any_int('z') == 26

def test_pySym_nestedWhile():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    assert pg.explore(find=14)
    assert pg.found[0].state.any_int('z') == 45

    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    assert pg.explore(find=14)
    assert pg.found[0].state.any_int('z') == 45



def test_pySym_funcInWhileTest():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    pg.explore()


    assert len(pg.active) == 0
    assert len(pg.completed) == 1
    assert len(pg.errored) == 0
    assert len(pg.deadended) == 6

    assert pg.completed[0].state.any_int('x') == 5


def test_pySym_simpleWhile():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    assert pg.explore(find=6)

    assert len(pg.active) == 0
    assert len(pg.completed) == 0
    assert len(pg.errored) == 0
    assert len(pg.deadended) == 11
    assert len(pg.found) == 1

    assert pg.found[0].state.isSat()
    assert pg.found[0].state.any_int('x') == 10

