import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
import pytest

test1 = "x = 1\ny = 2"

simpleIf = """
x = 1
y = 1
if x > y:
    print("This shouldn't hit")
else:
    print("This should hit")
    x = 2
"""

testIfReturn = """
x = 1
y = 1.2
if y > x:
    x += 1
else:
    x -= 1

y += 1
"""

def test_ifReturn():
    b = ast_parse.parse(testIfReturn).body
    p = Path(b,source=testIfReturn)
    p = p.step()[0].step()[0]
    ifSide,elseSide = p.step()
    ifSide = ifSide.step()[0].step()[0]
    elseSide = elseSide.step()[0].step()[0]
    
    assert ifSide.state.any_int('x') == 2
    assert ifSide.state.any_real('y') == 2.2
    assert elseSide.state.any_int('x') == None
    assert elseSide.state.any_real('y') == None # Else side is wonky because it's not a possible path


def test_basicPathStep():
    b = ast_parse.parse(test1).body
    p1 = Path(b,source=test1)
    p2 = p1.step()[0].step()[0]
    p1.printBacktrace()
    p2.printBacktrace()
    assert p2.state.any_int('x') == 1
    assert p2.state.any_int('y') == 2
    with pytest.raises(Exception):
        p1.state.any_int('x')
    with pytest.raises(Exception):
        p1.state.any_int('y')

def test_pathCopy():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    p2 = p.copy()
    assert p2 != p
    p = p.step()[0]
    assert p.state.any_int('x') == 1
    with pytest.raises(Exception):
        p2.state.any_int('x')

def test_simpleIf():
    b = ast_parse.parse(simpleIf).body
    p = Path(b,source=simpleIf)
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]
    
    # ifSide's path should now be inside, meaning only the print statement
    assert len(ifSide.state.path) == 1
    # Else should be in the else statement
    assert len(elseSide.state.path) == 2
    
    # Neither have anything to do after the if statement
    assert len(ifSide.state.callStack) == 1
    assert len(elseSide.state.callStack) == 0
    
    # If side should not be possible
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()
    
    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3
    
    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1
