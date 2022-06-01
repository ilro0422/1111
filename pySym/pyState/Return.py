import logging
import z3
import ast
from .. import pyState

logger = logging.getLogger("pyState:Return")

def handle(state,element):
    """Attempt to handle the Python Return element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Return
        element from source to be handled


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    
    
    This function handles calls to ast.Return. It is not meant to be
    called manually via a user. Under the hood, it resolves the return element,
    sets the ReturnObject, and updates the state.


    Example
    -------
    Example of ast.Return is: return x
    """

    
    assert type(state) == pyState.State
    assert type(element) == ast.Return

    ret = state.Return(element)
    
    logger.debug("handle: ret value = {0}".format(ret))

    # Normalize
    ret = [ret] if type(ret) is not list else ret

    # Check for return object. Return all applicable
    retObjs = [x.state for x in ret if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    # Asserting 1 thing to return for now
    assert len(ret) == 1
    obj = ret[0]

    state = obj.state if obj is not None else state

    # Pop callstacks until we change context
    leavingCtx = state.ctx
    
    # Pop until we've left
    while leavingCtx == state.ctx:

        state.popCallStack()

    return [state]
    
