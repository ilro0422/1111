import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')
import logging
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

from pySym import ast_parse
import z3
from pySym.pyState import State
import pytest
from pySym.pyPath import Path
from pySym.pyPathGroup import PathGroup
from pySym.pyObjectManager.Int import Int
from pySym.pyObjectManager.Real import Real
from pySym.pyObjectManager.BitVec import BitVec
from pySym.pyState import z3Helpers

test1 = "x = 1"
test2 = "x = 2"
test3 = "x = 3.1415"
test4 = """
x = pyState.Int()
"""
test5 = """
x = pyState.Real()
"""

test6 = """
i = pyState.BVV(123,64)
l = [1,2.2,3.1415,4,i,8,[1,2,3]]
"""

test7 = """
l = ["a","b","c"]
"""

test8 = """
s = pyState.String(8)
x = s.index('a')
"""

test9 = """
s = pyState.String(2)
x = "testt".rstrip(s)[-1]
"""

test10 = """
i = pyState.Int()
"""

test11 = """
def test():
    return VAR

def test2():
    q = 12
    def test3():
        return q
    return test3()

def test4():
    z = 1337
    def test5():
        def test6():
            return z
        return test6()
    return test5()

def test7():
    return VAR_LIST

VAR_LIST = [1,2,3,4]
VAR = "blerg"
ret = test() # Should be 'blerg'
ret2 = test2() # Should be 12
ret3 = test4() # Should be 1337
ret4 = test7() # Should be [1,2,3,4]
"""

def test_state_is_sat_extra_constraints():
    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()

    i = s.getVar('i')

    assert len(s.solver.assertions()) == 0
    assert s.isSat()
    assert s.isSat(extra_constraints=[i.getZ3Object() > 5])
    assert not s.isSat(extra_constraints=[i.getZ3Object() > 5, i.getZ3Object() == 3])
    assert len(s.solver.assertions()) == 0
    s.addConstraint(i.getZ3Object() > 5)
    assert len(s.solver.assertions()) == 1
    assert not s.isSat(extra_constraints=[i.getZ3Object() == 1])
    assert len(s.solver.assertions()) == 1

def test_state_track_var():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()
    
    # Add a new constraint
    x = s.getVar('x')
    z3_obj = x.getZ3Object()
    s.addConstraint(z3_obj > 5)
    #assert str(z3_obj) in s._vars_in_solver
    assert s.var_in_solver(z3_obj)

    # Remove the constraint
    s.remove_constraints(z3_obj > 5)
    #assert str(z3_obj) not in s._vars_in_solver
    assert not s.var_in_solver(z3_obj)


def test_state_add_multiple_constraints():
    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()
    i = s.getVar('i')
    z = i.getZ3Object()

    s.addConstraint(z > 12, z < 14)

    assert len(s.solver.assertions()) == 2
    assert int(i) == 13


def test_state_variable_inheritance():
    b = ast_parse.parse(test11).body
    p = Path(b,source=test11)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    ret = s.getVar('ret')
    assert ret.mustBe('blerg')
    assert s.getVar('ret2').mustBe(12)
    assert s.getVar('ret3').mustBe(1337)
    assert s.getVar('ret4')[0].mustBe(1)
    assert s.getVar('ret4')[1].mustBe(2)
    assert s.getVar('ret4')[2].mustBe(3)
    assert s.getVar('ret4')[3].mustBe(4)

def test_var_used_in_z3_ignore():
    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1

    s = pg.completed[0].state.copy()
    i = s.getVar('i')
    z3_obj = i.getZ3Object()

    # Not in here to begin with
    #assert not z3Helpers.varIsUsedInSolver(z3_obj,s.solver)
    assert not s.var_in_solver(z3_obj)

    # Now it will be in there
    s.addConstraint(z3_obj > 3)
    #assert z3Helpers.varIsUsedInSolver(z3_obj,s.solver)
    assert s.var_in_solver(z3_obj)

    # Now try ignoring it
    s.remove_constraints(z3_obj > 3)
    s.addConstraint(z3_obj > 3)
    assert not s.var_in_solver(z3_obj, ignore=[z3_obj > 3])
    assert not s.var_in_solver(z3_obj, ignore=z3_obj > 3)

def test_remove_constraints():
    b = ast_parse.parse(test10).body
    p = Path(b,source=test10)
    pg = PathGroup(p)
    
    pg.explore()

    s = pg.completed[0].state.copy()
    i = s.getVar('i')
    
    z = i.getZ3Object()

    # Adding a constraint then removing it
    const = z<22
    s.addConstraint(const)
    assert not i.canBe(30)
    assert s.remove_constraints(const) == 1
    assert i.canBe(30)


def test_extra_constraints():
    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 1
    state = pg.completed[0].state.copy()
    solver = state.solver
    num_assert = len(solver.assertions())
    x = state.getVar('x')
    i = state.any_int(x)
    assert state.any_int(x, extra_constraints=x.getZ3Object() != i) != i
    assert len(solver.assertions()) == num_assert
    assert state.any_int(x, extra_constraints=[x.getZ3Object() != i]) != i
    assert len(solver.assertions()) == num_assert


def test_assign_statetrack():
    b = ast_parse.parse(test9).body
    p = Path(b,source=test9)
    pg = PathGroup(p)
    
    pg.explore()

    assert len(pg.completed) == 5
    o = [p.state.any_str('x') for p in pg.completed]
    o.sort()
    assert o == ['e', 'e', 's', 's', 't']


def test_assign_stateSplit():
    b = ast_parse.parse(test8).body
    p = Path(b,source=test8)
    pg = PathGroup(p)
    
    pg.explore()
    
    assert len(pg.completed) == 8
    assert set([p.state.any_int('x') for p in pg.completed]) == set([x for x in range(8)])


def test_list_with_strings():
    b = ast_parse.parse(test7).body
    p = Path(b,source=test7)
    pg = PathGroup(p)
    
    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_list('l') == ["a","b","c"]


def test_recursiveCopy():
    b = ast_parse.parse(test6).body
    p = Path(b,source=test6)
    pg = PathGroup(p)
    
    pg.explore()
    
    assert len(pg.completed) == 1

    s = pg.completed[0].state

    l = s.getVar('l')
    l2 = s.recursiveCopy(s.getVar('l'))
    
    assert l != l2
    
    l2[-1][2].value = 4
    
    assert l[-1][2].value != l2[-1][2].value


def test_any_n_real():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)
    
    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_real('x') == 3.1415
    # Duplicate test to ensure we're not destroying state
    assert pg.completed[0].state.any_n_real('x',10) == [3.1415]
    assert pg.completed[0].state.any_n_real('x',10) == [3.1415]

    b = ast_parse.parse(test5).body
    p = Path(b,source=test5)
    pg = PathGroup(p)

    pg.explore()

    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_real('x') != None
    # Duplicate test to ensure we're not destroying state
    assert len(pg.completed[0].state.any_n_real('x',10)) == 10
    assert len(pg.completed[0].state.any_n_real('x',10)) == 10


def test_any_n_int():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    
    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') == 1
    # Duplicate test to ensure we're not destroying state
    assert pg.completed[0].state.any_n_int('x',10) == [1]
    assert pg.completed[0].state.any_n_int('x',10) == [1]

    b = ast_parse.parse(test4).body
    p = Path(b,source=test4)
    pg = PathGroup(p)
    
    pg.explore()
    
    assert len(pg.completed) == 1
    assert pg.completed[0].state.any_int('x') != None
    # Duplicate test to ensure we're not destroying state
    assert len(pg.completed[0].state.any_n_int('x',10)) == 10
    assert len(pg.completed[0].state.any_n_int('x',10)) == 10


def test_assignInt():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)
    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state
    # Basic dict checks
    assert type(s.getVar("x")) == Int
    assert s.getVar("x").getZ3Object().is_int()
    #assert len(s.solver.assertions()) == 1

    # Try solving it to ensure that works correctly
    assert s.isSat()
    
    # Ensure we're getting expected output
    assert s.any_int('x') == 1
    
    # Try assigning again
    b = ast_parse.parse(test2).body
    p = Path(b,source=test2)
    pg = PathGroup(p)
    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state
    
    # Basic dict checks
    assert type(s.getVar("x")) == Int
    assert s.getVar("x").getZ3Object().is_int()
    #assert len(s.solver.assertions()) == 2

    # Try solving it to ensure that works correctly
    assert s.isSat()
    
    # Ensure we're getting expected output
    assert s.any_int('x') == 2


def test_assignFloat():
    b = ast_parse.parse(test3).body
    p = Path(b,source=test3)
    pg = PathGroup(p)
    pg.explore()
    assert len(pg.completed) == 1

    s = pg.completed[0].state

    # Basic dict checks
    assert type(s.getVar("x")) == Real
    assert s.getVar("x").getZ3Object().is_real()
    #assert len(s.solver.assertions()) == 1

    # Try solving it to ensure that works correctly
    assert s.isSat()

    # This isn't an int, it will raise exception
    with pytest.raises(Exception):
       s.any_int('x')
    
    # We should get this back
    assert s.any_real('x') == 3.1415

def test_copy():
    b = ast_parse.parse("a = 1").body
    p = Path(b,source="a = 1")

    s = p.state
    s2 = s.copy()
    
    # Ensure it's actually being copied
    assert s != s2
    
    # Add something to one and make sure the other is empty
    #pyState.Assign.handle(s,assign)
    s = s.step()[0]
    assert s.any_int('a') == 1
    with pytest.raises(Exception):
        s2.any_int('a')
    #assert s.objectManager.variables != {0: {}, 1: {'ret': {'count': 0, 'varType': 'z3.IntSort()'}}}
    #assert s2.objectManager.localVars == {0: {}, 1: {'ret': {'count': 0, 'varType': 'z3.IntSort()'}}}

def test_any_int():
    b = ast_parse.parse("x = 12").body
    p = Path(b,source="x = 12")
    pg = PathGroup(p)
    pg.explore()
    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_int('x') == 12
    with pytest.raises(Exception):
        s.any_int('q') == None
    

def test_getZ3Object():
    b = ast_parse.parse("x = 12").body
    p = Path(b,source="x = 12")
    pg = PathGroup(p)
    pg.explore()
    assert len(pg.completed) == 1
    x = pg.completed[0].state.getVar('x')
    assert type(x) is Int
    
