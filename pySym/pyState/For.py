import logging
import z3
import ast
from .. import pyState
from ..pyObjectManager.List import List
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Real import Real
from ..pyObjectManager.BitVec import BitVec
from ..pyObjectManager.String import String
from ..pyObjectManager.Char import Char
from copy import copy

logger = logging.getLogger("pyState:For")


def _handle(state,element,newIter):

    # The For element is an iterator that sets variables
    iterator = element.iter
    target = element.target


    # Keep track of if we're just repeating a loop
    #newLoop = True if newIter != iterator else False
    newLoop = True if type(iterator) not in [List, String] else False

    # If it's a new loop, work on a copy not the real thing
    if newLoop:
        newIter = state.recursiveCopy(newIter)

    if type(newIter) not in [List, String]:
        err = "handle: I don't know how to handle iter type {0}".format(type(newIter))
        logger.error(err)
        raise Exception(err)

    # Moving forward
    state.path.pop(0)

    # Assuming it's a list for now

    # If we're out of things to iterate, take the else
    if len(newIter) == 0:
        cs = copy(state.path) #[copy(x) for x in state.path]
        if len(cs) > 0:
            state.pushCallStack(path=cs)

        # else side should be done with the loop
        state.loop = None
        state.path = element.orelse
        return [state]

    # If we're here, we have something left to do
    # Pop the current iter value
    elm = newIter.pop(0)

    # Set the iter back
    element.iter = newIter

    # Setup our callstack for this loop
    cs = copy(state.path) 

    # Don't want to push an empth path into call stack for now
    # If this is a new loop, save the previous info
    # TODO: Kinda hackish..
    if newLoop:
        if len(cs) ==  0:
            cs.append(ast.Pass(lineno=0,col_offset=0))
        state.pushCallStack(path=cs)

    # Our new path becomes the inside of the if statement
    state.path = element.body

    # If state should get a copy of the loop we're now in
    state.loop = element 


    # Create the target var
    t, kwargs = pyState.duplicateSort(elm)
    targets = state.resolveObject(target,varType=t,kwargs=kwargs)
    #target.increment()
    ret = []    

    for target in targets:

        target.increment()
    
        if type(target) in [Int, Real, BitVec, Char]:
            # Copy the constraint
            #target.state.addConstraint(target.getZ3Object() == elm.getZ3Object())
            target.setTo(elm)

        elif type(target) in [String, List]:
            target.setTo(elm,clear=True)

        else:
            err = "handle: I don't know how to handle target type {0}".format(type(target))
            logger.error(err)
            raise Exception(err)

        ret.append(target.state)

    return ret

def handle(state,element):
    """Attempt to handle the Python For element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.For
        element from source to be handled


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    

    This function handles calls to ast.For. It is not meant to be called
    manually via a user.


    Example
    -------
    Example of ast.For is: for x in [1,2,3]
    """

    assert type(element) is ast.For

    
    # The For element is an iterator that sets variables
    iterator = element.iter
    target = element.target
    
    # Resolve our iter first
    newIters = state.resolveObject(iterator)

    # Normalize
    newIters = [newIters] if type(newIters) is not list else newIters

    # Resolve calls if we need to
    retObjs = [x.state for x in newIters if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    for newIter in newIters:
        ret += _handle(state.copy(),copy(element),newIter)

    return ret

