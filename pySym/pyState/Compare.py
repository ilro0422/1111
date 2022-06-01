import logging
import z3
import ast
from .. import pyState
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Real import Real
from ..pyObjectManager.BitVec import BitVec
from ..pyObjectManager.Char import Char
from ..pyObjectManager.String import String


logger = logging.getLogger("pyState:Compare")

def _handleLeftVarInt(state,element,left):
    """
    Input:
        state = State object for the evaluation of the compare
        element = ast element object for the if statement (type ast.If)
        left = Left variable name or int (i.e.: 'x' or 5)
    Action:
        Handle compare where left side is a variable or int
        Note: left is treated as an object and used directly in the constraint.
              therefor it must be either an int or a z3 object type
        ex: if x > 5
    Return:
        Created constraint expressions for True state, or ReturnObject if we're waiting on a call
    """

    # Resolve the z3 object
    if type(left) in [Int, Real, BitVec, Char]:
        pass
        #left = left.getZ3Object()
    
    # If this is a String, let's hope it's only one char...
    elif type(left) is String and len(left) == 1:
        #left = left[0].getZ3Object()
        left = left[0]
    
    else:
        err = "_handleLeftVar: Don't know how to handle type '{0}'".format(type(left))
        logger.error(err)
        raise Exception(err)


    # Operators that we're comparing with
    ops = element.ops
    comp = element.comparators
    
    if len(ops) > 1 or len(comp) > 1:
        err = "_handleLeftVar: Don't know how to handle multiple operations '{0}' at line {1} column {2}".format(ops,element.lineno,element.col_offset)
        logger.error(err)
        raise Exception(err)
    
    ops = ops[0]
    comp = comp[0]
    
    right = state.resolveObject(comp)
   
    # normalize to list
    right = right if type(right) is list else [right]
     
    # Resolve calls if we need to
    retObjs = [x for x in right if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    # Loop through all the possible states
    for r in right:

        if type(r) in [Int, Real, BitVec, Char]:
            pass #r = r.getZ3Object()

        # If this is a String, let's hope it's only one char...
        elif type(r) is String and len(r) == 1:
            r = r[0]
            #r = r[0].getZ3Object()

        else:
            err = "_handleLeftVar: Don't know how to handle type '{0}'".format(type(r))
            logger.error(err)
            raise Exception(err)


        # Adjust the types if needed
        lz3,rz3 = pyState.z3Helpers.z3_matchLeftAndRight(left,r,ops)
        
        logger.debug("_handleLeftVar: Comparing {0} (type: {2}) and {1} (type: {3})".format(lz3,rz3,type(lz3),type(rz3)))
    
        # Assume success. Add constraints
        if type(ops) == ast.Gt:
            # Don't clutter up z3!
            if left.isStatic() and r.isStatic():
                ret += [left.getValue() > r.getValue()]
            else:
                ret += [lz3 > rz3]
        
        elif type(ops) == ast.GtE:
            # Don't clutter up z3!
            if left.isStatic() and r.isStatic():
                ret += [left.getValue() >= r.getValue()]
            else:
                ret += [lz3 >= rz3]
    
        elif type(ops) == ast.Lt:
            # Don't clutter up z3!
            if left.isStatic() and r.isStatic():
                ret += [left.getValue() < r.getValue()]
            else:
                ret += [lz3 < rz3]
    
        elif type(ops) == ast.LtE:
            # Don't clutter up z3!
            if left.isStatic() and r.isStatic():
                ret += [left.getValue() <= r.getValue()]
            else:
                ret += [lz3 <= rz3]
    
        elif type(ops) == ast.Eq:
            # Don't clutter up z3!
            if left.isStatic() and r.isStatic():
                ret += [left.getValue() == r.getValue()]
            else:
                ret += [lz3 == rz3]
    
        elif type(ops) == ast.NotEq:
            # Don't clutter up z3!
            if left.isStatic() and r.isStatic():
                ret += [left.getValue() != r.getValue()]
            else:
                ret += [lz3 != rz3]
    
        else:
            err = "_handleLeftVar: Don't know how to handle type '{0}' at line {1} column {2}".format(type(ops),element.lineno,element.col_offset)
            logger.error(err)
            raise Exception(err)
       
    return ret
    

def handle(state,element,ctx=None):
    """Attempt to handle the Python Compare element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Compare
        element from source to be handled
    ctx : int, optional
        `ctx` is an optional input to specify a context to be used
        when resolving this ast object


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. -- or -- list contains True constraints derived from
        input ast element as z3 elements.
    

    This function handles calls to ast.Compare. It is not meant to be called
    manually via a user.


    Example
    -------
    Example of ast.Compare is: 1 < 2
    """

    assert type(element) == ast.Compare
    
    ctx = ctx if ctx is not None else state.ctx

    # The left side of the compare
    left = element.left

    # Resolve it
    left = state.resolveObject(left,ctx=ctx)

    # Normalize to a list
    left = [left] if type(left) is not list else left

    # Resolve calls if we need to
    retObjs = [x for x in left if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    # Loop through possibilities
    for l in left:
    
        # TODO: Probably need to add checks or consolidate here...
        ret += _handleLeftVarInt(state,element,l)

    return ret
