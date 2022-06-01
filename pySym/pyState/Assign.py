import logging
import z3, z3.z3util as z3util
import ast
import os
#from . import hasRealComponent, ReturnObject, duplicateSort
#from pySym import pyState.BinOp, pyState.Call
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Real import Real
from ..pyObjectManager.BitVec import BitVec
from ..pyObjectManager.List import List
from ..pyObjectManager.String import String
from ..pyObjectManager.Char import Char

logger = logging.getLogger("pyState:Assign")


def _handleAssignNum(target,value):
    """
    Handle assigning a number to a variable (i.e.: x = 1)
    Update local variable dict and return
    value should already be resolved via state.resolveObject (meaning it is now a pyObjectManager object such as pyObjectManager.Int.Int)
    """

    # Implicitly taking value's state
    state = value.state.copy()
    #state = state.copy()

    logger.debug("_handleAssignNum: Handling {0} = {1}".format(type(target),type(value)))

    varType,kwargs = duplicateSort(value)

    x = state.resolveObject(target,varType=varType,kwargs=kwargs)
    
    """
    if type(value) is Real:
        x = state.resolveObject(target,varType=Real)

    elif type(value) is BitVec:
        x = state.resolveObject(target,varType=BitVec,kwargs={'size':value.size})

    else:
        x = state.resolveObject(target,varType=Int)
    """

    ret = []

    for x2 in x:

        """
        parent = x2.state.objectManager.getParent(x2)
        index = parent.index(x2)
        parent[index] = value
        """
        # Get a new variable assignment since we're...assigning...
        x2.increment()

        x2.setTo(value)
        x2.state = x2.state.copy()

        x2.state.path.pop(0)

        # Return the state
        ret += [x2.state]
    
    return ret


def _handleAssignList(target,listObject):
    assert type(target) is ast.Name
    assert type(listObject) is List 

    state = listObject.state.copy()

    # Resolve the object
    targets = state.resolveObject(target,varType=List)

    ret = []

    for target in targets:

        parent = state.objectManager.getParent(target)
        index = parent.index(target)

        # Set the new list
        parent[index] = listObject.copy()

        target.state = target.state.copy()

        target.state.path.pop(0)

        ret += [target.state]

    return ret

def _handleAssignString(target,stringObject):
    assert type(stringObject) in [String, Char]

    state = stringObject.state.copy()

    if type(stringObject) is Char:
        c = stringObject
        stringObject = state.getVar('tmpString',varType=String)
        stringObject.increment()
        stringObject.variables = [c]

    # Resolve the object
    targets = state.resolveObject(target,varType=String)

    ret = []

    for target in targets:
        state = target.state.copy()
        state.path.pop(0)

        parent = state.objectManager.getParent(target)
        index = parent.index(target)

        # Set the new list
        new_obj = stringObject.copy()
        # HACK! Sometimes the string doesn't end up with a new unique uuid... This is a hack around that for now.
        new_obj.uuid = os.urandom(32) 
        #parent[index] = stringObject.copy()
        parent[index] = new_obj
        #target.setTo(stringObject.copy(),clear=True)

        #target.state = target.state.copy()
        #target.state.path.pop(0)

        #ret += [target.state]
        ret += [state.copy()]
    
    return ret


def handle(state,element):
    """Attempt to handle the Python Assign element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.Assign
        element from source to be handled

    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast.

    
    This function handles calls to Assign. It is not meant to be called
    manually via a user.


    Example
    -------
    Example of ast.Assign is: x = 1
    """
    # Targets are what is being set
    targets = element.targets

    # Value is what to set them to
    value = element.value

    # Only handling single targets for now
    if len(targets) != 1:
        err = "Cannot handle multiple variable set at Line {0} Col {1}".format(element.lineno,element.col_offset)
        logger.error(err)
        raise Exception(err)

    # Clear up the naming
    target = targets[0]
    
    # Resolve the value
    values = state.resolveObject(value)

    # Normalize
    values = values if type(values) is list else [values]

    # Check for return object. Return all applicable
    retObjs = [x.state for x in values if type(x) is ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []
    
    # For every possible assign value, get the state
    for value in values:
        if type(value) in [Int, Real, BitVec]:
            ret += _handleAssignNum(target,value)
    
        elif type(value) is List:
            ret += _handleAssignList(target,value)
    
        elif type(value) in [String, Char]:
            ret += _handleAssignString(target,value)
    
        else:
            err = "Don't know how to assign type {0}".format(type(value))
            logger.error(err)
            raise Exception(err)

    return ret

from . import ReturnObject, duplicateSort
