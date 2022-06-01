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

test1 = """
def test2():
    return 5

def test():
    return test2() + test2()

x = test()
z = 1
"""

test2 = """
def test():
    return 5 + 1.5

x = test()

if x > 5:
    x = 1
else:
    x = 0

if x == 1:
    x = 1337

z = 1
"""

test3 = """
def test():
    return 5

if test() == 5.0:
    x = 1
else:
    x = 0

q = 5
"""

test4 = """
s = "A"*16

for c in s:
    if c == "A":
        q = 1
    else:
        q = 2
"""

def test_pyPathGroup_ignore_paths():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p,ignore_groups=['deadended'])

    # Execute to the end
    pg.explore()

    assert len(pg.completed) == 1
    assert len(pg.deadended) == 0


def test_pyPathGroup_exploreFunctionCompare():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)

    # Execute to the end
    assert pg.explore(find=10)
    
    assert len(pg.active) == 0
    assert len(pg.completed) == 0
    assert len(pg.errored) == 0
    assert len(pg.deadended) == 1
    assert len(pg.found) == 1

    assert pg.found[0].state.any_int('x') == 1
    

def test_pyPathGroup_exploreWithIf():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    
    # Explore to the end
    assert pg.explore(find=15)
    
    assert len(pg.active) == 0
    assert len(pg.completed) == 0
    assert len(pg.errored) == 0
    assert len(pg.deadended) == 2
    assert len(pg.found) == 1

    assert pg.found[0].state.any_int('x') == 1337


def test_pyPath_exploreFindLine():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    # Explore to line 9 (z = 1)
    # Current setup means that z=1 will not actually be executed
    assert pg.explore(find=9)
    
    assert len(pg.active) == 0
    assert len(pg.completed) == 0
    assert len(pg.errored) == 0
    assert len(pg.deadended) == 0
    assert len(pg.found) == 1

    assert pg.found[0].state.any_int('x') == 10


def test_pyPath_stepThroughProgram():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    pg.explore()

    assert len(pg.active) == 0
    assert len(pg.completed) == 1
    assert len(pg.errored) == 0
    assert len(pg.deadended) == 0
    assert len(pg.found) == 0
    
    assert pg.completed[0].state.any_int('x') == 10
    assert pg.completed[0].state.any_int('z') == 1

