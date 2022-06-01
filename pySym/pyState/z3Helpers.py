"""
A file to hold my helper items directly relating to z3
"""

import z3
from z3.z3 import _coerce_exprs
import ast
from .. import pyState
import logging
from ..pyObjectManager.BitVec import BitVec
from ..pyObjectManager.Real import Real
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Char import Char

logger = logging.getLogger("pyState:z3Helpers")

Z3_DEFAULT_BITVEC_SIZE = 64
Z3_MAX_STRING_LENGTH = 256

"""
def varIsUsedInSolver(var,solver,ignore=None):
    " ""
    Determine if the given var (z3 object) is used in solver. Optionally ignore a list of constraints.
    " ""
    logger.warn("varIsUsedInSolver is deprecated. Use solver.var_in_solver instead")

    ignore = [] if ignore is None else ignore

    # If it's a solo constraint, make it a list
    if type(ignore) is not None and type(ignore) not in [list, tuple]:
        ignore = [ignore]

    # Sanity check
    assert isZ3Object(var), "Expected var to be z3 object, got type {} instead".format(type(var))
    assert isinstance(solver,z3.Solver), "Solver must be type z3.Solver, got type {}".format(type(z3.Solver))

    # Remove any ignored assertions
    assertions = [ass for ass in solver.assertions() if ass not in ignore]

    for ass in assertions:
        if var.get_id() in [x.get_id() for x in pyState.get_all(ass)]:
            return True

    return False
"""


def isInt(x):
    """Wraps Z3 C API to perform isInt check on Real object x
    
    Parameters
    ----------
    x : z3.ArithRef or z3.RatNumRef
        Real variable from calls like z3.Real('x')


    Returns
    -------
    z3.BoolRef
        z3.BoolRef asserting type x is Int (i.e.: ends in .0)
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of isInt. The returned value is a boolean that the input Real type x is
    an integer (i.e.: ends in .0). This call is the C API that performs the
    check at solve time, rather than entry time.


    Example
    -------
    If you want to verify that Real type x is an Int::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x = z3.Real('x')
    
        In [5]: s.add(pyState.z3Helpers.isInt(x))
    
        In [6]: s.add(x == 5.0)
    
        In [7]: s
        Out[7]: [IsInt(x), x == 5]
    
        In [8]: s.check()
        Out[8]: sat

    """
    return z3.BoolRef(z3.Z3_mk_is_int(x.ctx_ref(),x.as_ast()))


#############################
# Watch for BitVec Overflow #
#############################

# TODO: Nikolaj went ahead and exposed this functionality directly in pyZ3 now. Update my stuff to use it
# https://github.com/Z3Prover/z3/commit/18200f55edf14e5360c9095736710ae689032f6d

def bvadd_safe(x, y, signed=False):
    """BitVector addition overflow/underflow checks
    
    Parameters
    ----------
    x,y : z3.BitVecRef or z3.BitVecNumRef
        These variables are the two BitVecs that will be added together.
    signed : bool, optional
        Should this addition be treated as signed?


    Returns
    -------
    tuple
        tuple of z3 solver constraints to detect an overflow or underflow
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of overflow and underflow checks. The returned tuple does not perform the
    addition, rather it is constraints that will perform the checks for overflow
    and underflow.


    Example
    -------
    If you want to verify the addition of x and y will not overflow/underflow::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x,y,z = z3.BitVecs('x y z',32)
    
        In [5]: s.add(pyState.z3Helpers.bvadd_safe(x,y))
    
        In [6]: s.add(x + y == z)
    
        In [7]: s
        Out[7]: 
        [Extract(32, 32, ZeroExt(1, x) + ZeroExt(1, y)) == 0,
         Implies(And(x < 0, y < 0), x + y < 0),
         x + y == z]
    
        In [8]: s.check()
        Out[8]: sat

    """

    assert x.ctx_ref()==y.ctx_ref()
    a, b = _coerce_exprs(x, y)
    return (z3.BoolRef(z3.Z3_mk_bvadd_no_overflow(a.ctx_ref(), a.as_ast(), b.as_ast(), signed)),
            z3.BoolRef(z3.Z3_mk_bvadd_no_underflow(a.ctx_ref(), a.as_ast(), b.as_ast())))

def bvmul_safe(x, y, signed=False):
    """BitVector multiplication overflow/underflow checks
    
    Parameters
    ----------
    x,y : z3.BitVecRef or z3.BitVecNumRef
        These variables are the two BitVecs that will be multiplied together.
    signed : bool, optional
        Should this multiplication be treated as signed?


    Returns
    -------
    tuple
        tuple of z3 solver constraints to detect an overflow or underflow
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of overflow and underflow checks. The returned tuple does not perform the
    multiplication, rather it is constraints that will perform the checks for overflow
    and underflow.


    Example
    -------
    If you want to verify the multiplication of x and y will not
    overflow/underflow::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x,y,z = z3.BitVecs('x y z',32)
    
        In [5]: s.add(pyState.z3Helpers.bvmul_safe(x,y))
    
        In [6]: s.add(x * y == z)
    
        In [7]: s
        Out[7]: [bvumul_noovfl(x, y), bvsmul_noudfl(x, y), x*y == z]
    
        In [8]: s.check()
        Out[8]: sat

    """

    assert x.ctx_ref()==y.ctx_ref()
    a, b = _coerce_exprs(x, y)
    return (z3.BoolRef(z3.Z3_mk_bvmul_no_overflow(a.ctx_ref(), a.as_ast(), b.as_ast(), signed)),
            z3.BoolRef(z3.Z3_mk_bvmul_no_underflow(a.ctx_ref(), a.as_ast(), b.as_ast())))

def bvsub_safe(x, y, signed=False):
    """BitVector subtraction overflow/underflow checks
    
    Parameters
    ----------
    x,y : z3.BitVecRef or z3.BitVecNumRef
        These variables are the two BitVecs that will be subtracted.
    signed : bool, optional
        Should this subtraction be treated as signed?


    Returns
    -------
    tuple
        tuple of z3 solver constraints to detect an overflow or underflow
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of overflow and underflow checks. The returned tuple does not perform the
    subtraction, rather it is constraints that will perform the checks for overflow
    and underflow.


    Example
    -------
    If you want to verify the subtraction of x and y will not
    overflow/underflow::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x,y,z = z3.BitVecs('x y z',32)
    
        In [5]: s.add(pyState.z3Helpers.bvsub_safe(x,y))
    
        In [6]: s.add(x - y == z)
    
        In [7]: s
        Out[7]: 
        [If(y == 1 << 31,
            x < 0,
            Implies(And(0 < x, 0 < -y), 0 < x + -y)),
         ULE(y, x),
         x - y == z]

    
        In [8]: s.check()
        Out[8]: sat

    """
    assert x.ctx_ref()==y.ctx_ref()
    a, b = _coerce_exprs(x, y)
    return (z3.BoolRef(z3.Z3_mk_bvsub_no_overflow(a.ctx_ref(), a.as_ast(), b.as_ast())),
            z3.BoolRef(z3.Z3_mk_bvsub_no_underflow(a.ctx_ref(), a.as_ast(), b.as_ast(), signed)))

def bvdiv_safe(x, y, signed=False):
    """BitVector division overflow check
    
    Parameters
    ----------
    x,y : z3.BitVecRef or z3.BitVecNumRef
        These variables are the two BitVecs that will be divided
    signed : bool, optional
        Should this division be treated as signed?


    Returns
    -------
    tuple
        tuple of z3 solver constraints to detect an overflow
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of overflow checks. The returned tuple does not perform the
    division, rather it is constraints that will perform the checks for
    overflow.


    Example
    -------
    If you want to verify the division of x and y will not
    overflow::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x,y,z = z3.BitVecs('x y z',32)
    
        In [5]: s.add(pyState.z3Helpers.bvdiv_safe(x,y))
    
        In [6]: s.add(x / y == z)
    
        In [7]: s
        Out[7]: [Not(And(x == 1 << 31, y == 4294967295)), x/y == z]
    
        In [8]: s.check()
        Out[8]: sat

    """
    assert x.ctx_ref()==y.ctx_ref()
    a, b = _coerce_exprs(x, y)
    return z3.BoolRef(z3.Z3_mk_bvsdiv_no_overflow(a.ctx_ref(), a.as_ast(), b.as_ast()))


def z3_bv_to_int(x):
    """BitVector to Integer Z3 conversion
    
    Parameters
    ----------
    x : z3.BitVecRef or z3.BitVecNumRef
        BitVector variable to be converted to Int


    Returns
    -------
    z3.ArithRef
        z3.ArithRef is an expression that will convert the BitVec into Integer
        inside Z3 rather than before insertion into the solver.
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of BitVec to Int conversions. The returned object is an expression that Z3
    will evaluate as an Int rather than BitVec during solving.


    Example
    -------
    If you want to convert a BitVec into an Int::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x = z3.BitVec('x',32)
    
        In [5]: y = z3.Int('y')

        In [6]: x = pyState.z3Helpers.z3_bv_to_int(x)
    
        In [7]: s.add(x == y)
    
        In [8]: s
        Out[8]: [BV2Int(x) == y] 
    
        In [9]: s.check()
        Out[9]: sat

    """
    return z3.ArithRef(z3.Z3_mk_bv2int(x.ctx_ref(), x.as_ast(), 0), x.ctx)

def z3_int_to_bv(x,size=Z3_DEFAULT_BITVEC_SIZE):
    """Integer to BitVector Z3 conversion
    
    Parameters
    ----------
    x : z3.ArithRef or z3.IntNumRef
        Int variable to be converted to BitVec
    size : int, optional
        BitVec bit size. If not specified, defaults to
        pyState.z3Helpers.Z3_DEFAULT_BITVEC_SIZE


    Returns
    -------
    z3.BitVecRef
        This is the BitVec reference for the associated Int
    
    
    This function wraps Z3 C API functions to allow for a python interpretation
    of Int to BitVec conversions. The returned object is an expression that Z3
    will evaluate as an BitVec rather than Int during solving.


    Example
    -------
    If you want to convert an Int int into a BitVec::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: s = z3.Solver()
    
        In [4]: x = z3.BitVec('x',8)
    
        In [5]: y = z3.Int('y')

        In [6]: y = pyState.z3Helpers.z3_int_to_bv(y,8)
    
        In [7]: s.add(x == y)
    
        In [8]: s
        Out[8]: [x == int2bv(y)]
    
        In [9]: s.check()
        Out[9]: sat

    """

    assert type(x) in [z3.IntNumRef,z3.ArithRef]
    assert x.is_int()
    # Converts Int to BV
    return z3.BitVecRef(z3.Z3_mk_int2bv(x.ctx_ref(),size,x.as_ast()))


def isZ3Object(obj):
    """Determine if the object given is a z3 type object
    
    Parameters
    ----------
    x : any
        Object can be any type


    Returns
    -------
    bool
        True if object is known z3 type, False otherwise
    
    
    This function is helpful if you want to verify that a given input object is
    a z3 type object. Under the cover, it runs the type operator against the
    object and compares it to known z3 types.

    Example
    -------
    If you want to verify x is a valid z3 object::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: x = z3.Real('x')
    
        In [4]: assert pyState.z3Helpers.isZ3Object(x)

    """
    # TODO: This isn't a very good solution...
    if type(obj) in [z3.ArithRef, z3.IntNumRef, z3.RatNumRef, z3.BitVecRef, z3.BitVecNumRef, z3.ArrayRef, z3.SeqRef]:
        return True
    return False

"""
def mk_var(name,vsort):
    "" "Determine if the object given is a z3 type object
    
    Parameters
    ----------
    x : any
        Object can be any type


    Returns
    -------
    bool
        True if object is known z3 type, False otherwise
    
    
    This function is helpful if you want to verify that a given input object is
    a z3 type object. Under the cover, it runs the type operator against the
    object and compares it to known z3 types.

    Example
    -------
    If you want to verify x is a valid z3 object::

        In [1]: import z3
    
        In [2]: from pySym import pyState.z3Helpers
    
        In [3]: x = z3.Real('x')
    
        In [4]: assert pyState.z3Helpers.isZ3Object(x)

    "" "
    if vsort.kind() == z3.Z3_INT_SORT:
        v = z3.Int(name)
    elif vsort.kind() == z3.Z3_REAL_SORT:
        v = z3.Real(name)
    elif vsort.kind() == z3.Z3_BOOL_SORT:
        v = z3.Bool(name)
    elif vsort.kind() == z3.Z3_DATATYPE_SORT:
        v = z3.Const(name,vsort)
    elif vsort.kind() == z3.Z3_BV_SORT:
        v = z3.BitVec(name,vsort.size())

    else:
        assert False, 'Cannot handle this sort (s: %sid: %d)'\
            %(vsort,vsort.kind())

    return v
"""

def z3_matchLeftAndRight(left,right,op):
    """Appropriately change the two variables so that they can be used in an
    expression
    
    Parameters
    ----------
    left,right : pyObjectManager.Int.Int or pyObjectManager.Real.Real or pyObjectManager.BitVec.BitVec or pyObjectManager.Char.Char
        Objects to be matched
    op : ast.*
        Operation that will be performed


    Returns
    -------
    tuple
        (z3ObjectLeft,z3ObjectRight) tuple of z3 objects that can be used in an expression
    
    
    The purpose of this function is to match two pyObjectManager.* variables to
    a given ast operation element. Z3 needs to have matched types, and this
    call will not only match the objects, but also attempt to concretize input
    wherever possible.

    Example
    -------
    If you want to auto-match BitVector sizes::

        In [1]: import z3, pyState.z3Helpers, ast
    
        In [2]: from pySym.pyObjectManager.BitVec import BitVec

        In [3]: from pySym.pyState import State

        In [4]: state = State()
    
        In [5]: x = BitVec("x",0,16,state=state)

        In [6]: y = BitVec("y",0,32,state=state)
    
        In [7]: l,r = pyState.z3Helpers.z3_matchLeftAndRight(x,y,ast.Add())

        In [8]: s = z3.Solver()

        In [9]: s.add(l + r == 12)

        In [10]: s
        Out[10]: [SignExt(16, 0x@0) + 0y@0 == 12]

        In [11]: s.check()
        Out[11]: sat

    """

    lType = type(left)
    rType = type(right)

    # If it's char, just grab the BitVec object
    if lType is Char:
        left = left.variable
        lType = type(left)
    if rType is Char:
        right = right.variable
        rType = type(right)

    logger.debug("z3_matchLeftAndRight: Called to match {0} and {1}".format(type(left),type(right)))
    needBitVec = True if type(op) in [ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift] else False
    # TODO: If the two sizes are different, we'll have problems down the road.
    bitVecSize = max([c.size for c in [b for b in [left,right] if type(b) is BitVec]],default=Z3_DEFAULT_BITVEC_SIZE)

    #####################################
    # Case: Both are already BitVectors #
    #####################################
    # Check length. Extend if needed.
    if type(left) is BitVec and type(right) is BitVec:
        logger.debug("z3_matchLeftAndRight: Matching BitVecLength @ {0} (left={1},right={2})".format(bitVecSize,left.size,right.size))
        if left.size < right.size:
            # Sign extend left's value to match
            left = z3.SignExt(right.size-left.size,left.getZ3Object())
            right = right.getZ3Object()
        elif right.size > left.size:
            right = z3.SignExt(left.size-right.size,right.getZ3Object())
            left = left.getZ3Object()
        
        # Sync-up the output variables
        left = left.getZ3Object() if type(left) in [Int, Real, BitVec] else left
        right = right.getZ3Object() if type(right) in [Int, Real, BitVec] else right

        logger.debug("z3_matchLeftAndRight: Returning {0} and {1}".format(type(left),type(right)))

        return left,right

    #####################################
    # Case: One is BitVec and one isn't #
    #####################################
    # For now only handling casting of int to BV. Not other way around.
    if (lType is BitVec and rType is Int) or (rType is Int and needBitVec):
        # If we need to convert to BitVec and it is a constant, not variable, do so more directly
        if right.isStatic():
            right = z3.BitVecVal(right.getValue(),bitVecSize)
        # Otherwise cast it. Not optimal, but oh well.
        else:
            right = z3_int_to_bv(right.getZ3Object(),size=bitVecSize)

    if (rType is BitVec and lType is Int) or (lType is Int and needBitVec):
        if left.isStatic():
            left = z3.BitVecVal(left.getValue(),bitVecSize)
        else:
            left = z3_int_to_bv(left.getZ3Object(),size=bitVecSize)
        
    ################################
    # Case: One is Int one is Real #
    ################################
    # So long as this isn't modular arithmetic, let's change to Real things
    if lType is Real and rType is Int and type(op) is not ast.Mod:
        if right.isStatic():
            right = z3.RealVal(right.getValue())
        else:
            # TODO: Z3 is really bad at handling these...
            right = z3.ToReal(right.getZ3Object())

    if rType is Real and lType is Int and type(op) is not ast.Mod:
        if left.isStatic():
            left = z3.RealVal(left.getValue())
        else:
            # TODO: Z3 is really bad at handling these...
            left = z3.ToReal(left.getZ3Object())


    ############################################
    # Case: One is Int one is Real for ast.Mod #
    ############################################
    # So long as this isn't modular arithmetic, let's change to Real things
    if lType is Real and rType is Int and type(op) is ast.Mod:
        if left.isStatic():
            leftVal = left.getValue()
            left = z3.IntVal(leftVal)
            if int(leftVal) != leftVal:
                logger.warn("Truncating value for Modular Arithmetic. That may or may not be what was intended!")

        # See if we can swing this the other direction
        elif right.isStatic():
            rightVal = right.getValue()
            right = z3.RealVal(rightVal)
            

    if rType is Real and lType is Int and type(op) is ast.Mod:
        if right.isStatic():
            rightVal = right.getValue()
            right = z3.IntVal(rightVal)
            if int(rightVal) != rightVal:
                logger.warn("Truncating value for Modular Arithmetic. That may or may not be what was intended!")

        # See if we can swing this the other direction
        else:
            left = z3.RealVal(left.getValue())
    
    # Sync-up the output variables
    left = left.getZ3Object() if type(left) in [Int, Real, BitVec] else left
    right = right.getZ3Object() if type(right) in [Int, Real, BitVec] else right

    logger.debug("z3_matchLeftAndRight: Returning {0} and {1}".format(type(left),type(right)))

    return left,right

