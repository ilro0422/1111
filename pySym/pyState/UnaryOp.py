import logging
import z3
import ast
from .. import pyState
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Real import Real
from ..pyObjectManager.BitVec import BitVec

logger = logging.getLogger("pyState:UnaryOp")

def handle(state,element,ctx=None):
    """Attempt to handle the Python UnaryOp element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.UnaryOp
        element from source to be handled
    ctx : int , optional
        Context to resolve this UnaryOp in (default is current context)


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    
    
    This function handles calls to ast.UnaryOp. It is not meant to be
    called manually via a user.


    Example
    -------
    Example of ast.UnaryOp is: not True
    """

    ctx = state.ctx if ctx is None else ctx
    
    assert type(state) == pyState.State
    assert type(element) == ast.UnaryOp

    op = element.op
    targets = state.resolveObject(element.operand)

    ret = []    
    
    for target in targets:

        # Use the target's state
        state = target.state

        if type(target) not in [Int, Real, BitVec]:
            err = "handle: unable to resolve UnaryOp target type '{0}'".format(type(target))
            logger.error(err)
            raise Exception(err)
    
        # Get a new variable
        t,args = pyState.duplicateSort(target)
        newVar = state.getVar("tempUnaryOp",varType=t,kwargs=args)
        newVar.increment()
    
        if type(op) == ast.USub:
            # Optimize if we can
            if target.isStatic():
                newVar.setTo(target.getValue() * -1)
            else:
                state.addConstraint(newVar.getZ3Object() == -target.getZ3Object())

        elif type(op) == ast.UAdd:
            #state.addConstraint(newVar.getZ3Object() == target.getZ3Object())
            newVar.setTo(target)

        elif type(op) == ast.Not:
            # TODO: Verify functionality here... Should be able to optimize like I did with the other two, but need to check how "Not" is being dealt with
            state.addConstraint(newVar.getZ3Object() == z3.Not(target.getZ3Object()))

        elif type(op) == ast.Invert:
            err = "handle: Invert not implemented yet"
            logger.error(err)
            raise Exception(err)

        else:
            # We really shouldn't get here...
            err = "handle: {0} not implemented yet".format(type(op))
            logger.error(err)
            raise Exception(err)

        ret.append(newVar.copy())

    return ret
