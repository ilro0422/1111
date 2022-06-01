import logging
import z3
import ast
from .. import pyState

logger = logging.getLogger("pyState:FunctionDef")

def handle(state,element):
    """Attempt to handle the Python FunctionDef element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.FunctionDef
        element from source to be handled


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    

    This function handles calls to ast.FunctionDef. It is not meant to be called
    manually via a user. Under the hood, it registers this function with the
    `state` object so that when it's referenced later it can be found.


    Example
    -------
    Example of ast.FunctionDef is: def test():
    """

    assert type(state) == pyState.State
    assert type(element) == ast.FunctionDef
    
    state.registerFunction(element)
    
    # Pop instruction
    state.path.pop(0)
    
    # Return state
    return [state]
