import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
from pySym.pyState import Compare
import pytest
from pySym.pyPathGroup import PathGroup

compare1 = """
x = {0}
y = {1}
if x {2} y:
    print("One")
else:
    print("Two")
    x = 7
"""

compare2 = """
x = {0}
y = 12
if x {2} {1}:
    print("One")
else:
    print("Two")
    x = 7
"""

compare3 = """
x = {0}
y = 12
if {1} {2} x: 
    print("One")
else:
    print("Two")
    x = 7
"""

compare4 = """
s = pyState.String(10)
if s[2] == 't':
    print("Yes")
"""

def test_pySym_Compare_Symbolic_String():
    b = ast_parse.parse(compare4).body
    p = Path(b,source=compare4)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 2

    assert pg.completed[1].state.any_str('s')[2] == "t"



def test_pySym_Compare():
    ################
    # Greater Than #
    ################
    b = ast_parse.parse(compare1.format(1,5,">")).body
    p = Path(b,source=compare1.format(1,5,">"))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should not be possible
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1

    #########################
    # Greater Than Or Equal #
    #########################
    b = ast_parse.parse(compare1.format(2,2,">=")).body
    p = Path(b,source=compare1.format(2,2,">="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 2
    assert elseSide.state.any_int('x') == None

    #############
    # Less Than #
    #############
    b = ast_parse.parse(compare1.format(1,5,"<")).body
    p = Path(b,source=compare1.format(1,5,"<"))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 1
    assert elseSide.state.any_int('x') == None

    ######################
    # Less Than Or Equal #
    ######################
    b = ast_parse.parse(compare1.format(3,5,"<=")).body
    p = Path(b,source=compare1.format(3,5,"<="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]
    
    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 3
    assert elseSide.state.any_int('x') == None

    #########
    # Equal #
    #########
    b = ast_parse.parse(compare1.format(1,5,"==")).body
    p = Path(b,source=compare1.format(1,5,"=="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should not be correct
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1

    #############
    # Not Equal #
    #############
    b = ast_parse.parse(compare1.format(1,5,"!=")).body
    p = Path(b,source=compare1.format(1,5,"!="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 1
    assert elseSide.state.any_int('x') == None


def test_unhandled_input():
    """
    This is admittedly contrived tests to just excersize code paths
    """
    class fakeElement:
        def __init__(self):
            self.ops = []
            self.comparators = []
    
    element = fakeElement()
    element.ops += ["test","test"]
    element.comparators += ["test","test"]
   
    # We aren't handling multiple comps/ops at this point 
    with pytest.raises(Exception):
        Compare._handleLeftVar(True,False,element,"x")


def test_pySym_CompareRightNum():
    ################
    # Greater Than #
    ################
    b = ast_parse.parse(compare2.format(1,5,">")).body
    p = Path(b,source=compare2.format(1,5,">"))
    # Step through the "if" statement
    p = p.step()[0]
    print(p.state.solver)
    p = p.step()[0]
    print(p.state.solver)
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]
    print(ifSide.state.solver)
    print(elseSide.state.solver)
    # If side should not be possible
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1

    #########################
    # Greater Than Or Equal #
    #########################
    b = ast_parse.parse(compare2.format(2,2,">=")).body
    p = Path(b,source=compare2.format(2,2,">="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 2
    assert elseSide.state.any_int('x') == None

    #############
    # Less Than #
    #############
    b = ast_parse.parse(compare2.format(1,5,"<")).body
    p = Path(b,source=compare2.format(1,5,"<"))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 1
    assert elseSide.state.any_int('x') == None

    ######################
    # Less Than Or Equal #
    ######################
    b = ast_parse.parse(compare2.format(3,5,"<=")).body
    p = Path(b,source=compare2.format(3,5,"<="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]
    
    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 3
    assert elseSide.state.any_int('x') == None

    #########
    # Equal #
    #########
    b = ast_parse.parse(compare2.format(1,5,"==")).body
    p = Path(b,source=compare2.format(1,5,"=="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should not be correct
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1

    #############
    # Not Equal #
    #############
    b = ast_parse.parse(compare2.format(1,5,"!=")).body
    p = Path(b,source=compare2.format(1,5,"!="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 1
    assert elseSide.state.any_int('x') == None


def test_pySym_CompareLeftNum():
    ################
    # Greater Than #
    ################
    b = ast_parse.parse(compare3.format(1,5,">")).body
    p = Path(b,source=compare3.format(1,5,">"))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]
    # If side should be right
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 1
    assert elseSide.state.any_int('x') == None

    #########################
    # Greater Than Or Equal #
    #########################
    b = ast_parse.parse(compare3.format(2,2,">=")).body
    p = Path(b,source=compare3.format(2,2,">="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 2
    assert elseSide.state.any_int('x') == None

    #############
    # Less Than #
    #############
    b = ast_parse.parse(compare3.format(1,5,"<")).body
    p = Path(b,source=compare3.format(1,5,"<"))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If else should be correct
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1

    ######################
    # Less Than Or Equal #
    ######################
    b = ast_parse.parse(compare3.format(3,5,"<=")).body
    p = Path(b,source=compare3.format(3,5,"<="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]
    
    # Else side should be correct
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 3

    #########
    # Equal #
    #########
    b = ast_parse.parse(compare3.format(1,5,"==")).body
    p = Path(b,source=compare3.format(1,5,"=="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should not be correct
    assert not ifSide.state.isSat()
    assert elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == None
    assert elseSide.state.any_int('x') == 1

    #############
    # Not Equal #
    #############
    b = ast_parse.parse(compare3.format(1,5,"!=")).body
    p = Path(b,source=compare3.format(1,5,"!="))
    # Step through the "if" statement
    p = p.step()[0]
    p = p.step()[0]
    p2 = p.step()
    ifSide = p2[0]
    elseSide = p2[1]

    # If side should be correct
    assert ifSide.state.isSat()
    assert not elseSide.state.isSat()

    # Track expected number of assertions
    #assert len(ifSide.state.solver.assertions()) == 3
    #assert len(elseSide.state.solver.assertions()) == 3

    # Make sure the answer makes sense
    assert ifSide.state.any_int('x') == 1
    assert elseSide.state.any_int('x') == None
