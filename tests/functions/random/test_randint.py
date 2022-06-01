import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))

import logging
from pySym import Colorer
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
from pySym.pyPathGroup import PathGroup
import pytest

test1 = """
r = random.randint(1337,31337)
"""

test2 = """
s = pyState.String(8)
r = random.randint(0, s.index('a'))
"""

def test_function_random_randint_statesplit():
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 8

    # Check where each state maxes out to ensure we're splitting right
    max_values = set()

    for path in pg.completed:

        r = path.state.getVar('r')

        for i in range(16):
            if not r.canBe(i):
                max_values.add(i-1)
                break
        else: 
            assert False, "Random went way out of range..."

    assert max_values == set([0,1,2,3,4,5,6,7])


def test_function_random_randint_basic():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    r = s.getVar('r')

    assert r.canBe(1337)
    assert r.canBe(31337)
    assert not r.canBe(31338)
    assert not r.canBe(1336)

