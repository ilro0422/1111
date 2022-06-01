import logging
import z3
import ast
from .. import pyState

logger = logging.getLogger("pyState:Pass")

def handle(state,element):
    """Attempt to handle the Python Pass element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Pass
        element from source to be handled


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    
    
    This function handles calls to ast.Pass. It is not meant to be
    called manually via a user. Under the hood, it very simply pops off the
    current instruction and returns the updated state object as a list.


    Example
    -------
    Example of ast.Pass is: pass
    """

    
    state.path.pop(0)
    
    return [state]
