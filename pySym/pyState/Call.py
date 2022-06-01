import logging
import z3
import ast
from .. import pyState
from copy import copy
import itertools

logger = logging.getLogger("pyState:Call")


def _resolveArgs(state,element):

    ret = []
    # Resolve the args
    for arg in element.args:
        caller_args = state.resolveObject(arg)

        # Normalize
        caller_args = [caller_args] if type(caller_args) is not list else caller_args

        # Check for return object. Return all applicable
        retObjs = [x for x in caller_args if type(x) is pyState.ReturnObject]
        if len(retObjs) > 0:
            return retObjs
        
        ret.append(caller_args)

    return itertools.product(*ret)

def _resolveKeywords(state,element):
    ret = []

    for keyword in element.keywords:
        kws = []
        caller_args = state.resolveObject(keyword.value)

        # Normalize
        caller_args = [caller_args] if type(caller_args) is not list else caller_args
        
        # Check for return object. Return all applicable
        retObjs = [x for x in caller_args if type(x) is pyState.ReturnObject]
        if len(retObjs) > 0:
            return retObjs

        # Add all of these to a list
        for arg in caller_args:
            kw = copy(keyword)
            kw.value = arg.copy()
            kws.append(kw)

        ret.append(kws)

    return itertools.product(*ret)

def handle(state,element,retObj=None):
    """Attempt to handle the Python Call element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Call
        element from source to be handled
    retObj : pyState.ReturnObject, optional
        `retObj` is an optional input to specify a ReturnObject to be used
        ahead of time.


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast.
    

    This function handles calls to ast.Call. It is not meant to be called
    manually via a user. A call will cause a context switch, populate
    variables, and set other internals. Upon return, the state will be inside the
    function.


    Example
    -------
    Example of ast.Call is: test()
    """

    assert type(state) == pyState.State
    assert type(element) == ast.Call

    argElements = list(_resolveArgs(state,element))

    # Check for return object. Return all applicable
    retObjs = [x for x in argElements if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    keywordElements = list(_resolveKeywords(state,copy(element)))

    # Check for return object. Return all applicable
    retObjs = [x for x in keywordElements if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = [] 

    # Yeah, this is a hack. But when we're soft matching, this number can help us identify the right thing.
    element.col_offset = 31337
    
    # For each possible combination of args
    for arg in argElements:
        
        for keyword in keywordElements:

            # Set the arg list
            elm = copy(element)
            elm.args = arg

            # Set the kwlist
            elm.keywords = keyword

            # Copy state
            s = state.copy()

            # Create our return object (temporary ID to be filled in by the Call handle)
            retObj = pyState.ReturnObject(1,s)

            # Update state, change call to ReturnObject so we can resolve next time
            assert pyState.replaceObjectWithObject(s.path[0],element,retObj)

            # Ensure everything has a correct state
            for a in elm.args:
                a.state = s

            for a in keyword:
                a.value.state = s

            # Call
            ret += [s.Call(elm,retObj=retObj)]
    
    return ret
    
