import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
import pytest

test1 = """
def test():
    x = 12

def test2(a,b,c):
    a = 13
"""


def test_pySym_FuncionDef():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    # Step through program
    p = p.step()[0]
    p = p.step()[0]
    # We should have two defs now
    assert "test" in p.state.functions
    assert "test2" in p.state.functions
