import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
import pytest

test1 = """
x = 4
pass
def test():
    x = 6
    return 5

x = test()
z = 1
"""


def test_pySym_pass():
    # Testing we can pass :-)
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    p = p.step()[0]
    p = p.step()[0]
    
    assert p.state.any_int('x') == 4
    assert len(p.state.backtrace) == 2


