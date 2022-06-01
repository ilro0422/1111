import logging
logger = logging.getLogger("pyState:Assert")

import z3
import ast
from . import Compare, BoolOp, ReturnObject
from copy import copy


def handle(state,element,ctx=None):
    """Attempt to handle the Python Assert element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Assert
        element from source to be handled
    ctx : int, optional
        `ctx` is an optional input to specify a context to be used
        when resolving this ast object


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    
    
    This function handles calls to ast.Assert. It is not meant to be
    called manually via a user. Under the hood, it resolves the conitional
    arguments, then asserts the truth of that statement on the state.


    Example
    -------
    Example of ast.Assert is: assert x > 5
    """

    # element.msg -- what to evaluate if assertion is wrong. It doesn't have to be a string, just some expression.
    
    # Check what type of test this is

    # Example: assert 4 > 2
    if type(element.test) == ast.Compare:
        constraints = Compare.handle(state, element.test, ctx=ctx)

    else:
        raise Exception("Assert: Unknown test type of '{0}'".format(type(element.test)))

    """
    # Example: assert False
    # TODO: Need to add ast.NameConstant resolution to resolveObject before implementing this.
    elif type(element.test) == ast.NameConstant:
        import IPython
        IPython.embed()
        exit(0)
    """

    #elif type(element.test) == ast.UnaryOp:
    #    trueConstraint = pyState.UnaryOp.handle(state, element.test)
    #    # This returns pyObjectManager objects, need to resolve the
    #    trueConstraint = [[x for x in constraint.state.assertions()][-1] for constraint in trueConstraint]

    # Resolve calls if we need to
    retObjs = [x.state for x in constraints if type(x) is ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    state.addConstraint(*constraints)

    # Not waiting on anything, move forward
    state.path.pop(0)
    
    return [state]
