import logging
import z3
import ast
from . import Compare, BoolOp, ReturnObject
from copy import copy

logger = logging.getLogger("pyState:If")


def _handleConstraints(stateIf,stateElse,trueConstraint,element):
    # Add the constraints we just got
    # Optimization to not add extra constraints
    if type(trueConstraint) is not bool or trueConstraint != True:
        stateIf.addConstraint(trueConstraint)
    if type(trueConstraint) is not bool or trueConstraint == True:
        stateElse.addConstraint(z3.Not(trueConstraint))

    ret_states = [stateIf,stateElse]

    # Check if statement. We'll have at least one instruction here, so treat this as a call
    # Saving off the current path so we can return to it and pick up at the next instruction
    cs = copy(stateIf.path)
    # Only push our stack if it's not empty
    if len(cs) == 0:
        cs.append(ast.Pass(lineno=0,col_offset=0))
    stateIf.pushCallStack(cs,stateIf.ctx,stateIf.retID)

    # Our new path becomes the inside of the if statement
    stateIf.path = element.body
    # Once inside the If, we're no longer in a "loop" for this call
    stateIf.loop = None

    # Update the else's path
    # Check if there is an else path we need to take
    if len(element.orelse) > 0:
        cs = copy(stateElse.path)
        if len(cs) > 0:
            stateElse.pushCallStack(cs,stateIf.ctx,stateIf.retID)

        stateElse.path = element.orelse
        stateElse.loop = None

    return ret_states


def handle(state,element):
    """Attempt to handle the Python If element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.If
        element from source to be handled


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    
    
    This function handles calls to ast.If. It is not meant to be
    called manually via a user. Under the hood, it resolves the conitional
    arguments, splits it's state, and takes both possibilities as the same time.


    Example
    -------
    Example of ast.If is: if x > 5:
    """

    
    # On If statements we want to take both options

    # path == we take the if statement
    stateIf = state

    # Check what type of test this is    
    if type(element.test) == ast.Compare:
        trueConstraint = Compare.handle(state,element.test)
        
    elif type(element.test) == ast.BoolOp:
        trueConstraint = BoolOp.handle(state, element.test)
    
    elif type(element.test) == ast.Call:
        trueConstraint = state.resolveObject(element.test)

    elif type(element.test) == ast.Subscript:
        #trueConstraint = state.resolveObject(element.test)
        objs = state.resolveObject(element.test)

        # Check for return object. Return all applicable
        retObjs = [x.state for x in objs if type(x) is ReturnObject]
        if len(retObjs) > 0:
            return retObjs

        trueConstraint = []

        # Usually will only be one, but you never know
        for obj in objs:

            # If it's an int of some sort
            if type(obj) in [Int, BitVec]:

                # Python defines 0 as being False for an int, everything else is True
                
                # If it's static, determine directly if we're true or not
                if obj.isStatic():
                    trueConstraint.append(obj.getValue() != 0)

                else:
                    trueConstraint.append(obj.getZ3Object() != 0)

            else:
                error = "Unhandled If Subscript object type of {}".format(type(obj))
                logger.error(error)
                raise Exception(error)

    #elif type(element.test) == ast.UnaryOp:
    #    trueConstraint = pyState.UnaryOp.handle(state, element.test)
    #    # This returns pyObjectManager objects, need to resolve the
    #    trueConstraint = [[x for x in constraint.state.assertions()][-1] for constraint in trueConstraint]

    else:
        err = "handle: I don't know how to handle type {0}".format(type(element.test))
        logger.error(err)
        raise Exception(err)


    # Normalize
    trueConstraint = trueConstraint if type(trueConstraint) is list else [trueConstraint]

    # Resolve calls if we need to
    retObjs = [x.state for x in trueConstraint if type(x) is ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    # Important to copy after Constraint generation since it may have added to the state!
    stateElse = state.copy()

    # Not waiting on anything, move forward
    stateIf.path.pop(0)
    stateElse.path.pop(0)
    
    ret = []

    for tc in trueConstraint:
        logger.debug("handling trueConstraint {0}".format(tc))
        ret += _handleConstraints(stateIf.copy(),stateElse.copy(),tc,element)
    
    return ret

from ..pyObjectManager.Int import Int
from ..pyObjectManager.BitVec import BitVec
