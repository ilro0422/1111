import logging
import z3
import ast
from .. import pyState

logger = logging.getLogger("pyState:Break")

def handle(state,element):
    """Attempt to handle the Python Break element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Break
        element from source to be handled

    Returns
    -------
    list
        list contains state objects either generated or discovered through handling this ast.
    

    This function handles calls to Break. It is not meant to be called
    manually via a user. Under the hood, it simply pops off the call stack
    until a loop change is seen (i.e.: we've left the for loop)


    Example
    -------
    Example of ast.Break is: break
    """

    assert type(state) == pyState.State
    assert type(element) == ast.Break

    # We could be in a few levels of if/else statements. Pop back up to the loop
    while state.loop == None:
        state.popCallStack()

    # Good to go, pop out of our loop
    state.popCallStack()

    return [state]
    
