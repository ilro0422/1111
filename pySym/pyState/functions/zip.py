from ...pyObjectManager.Int import Int
from ...pyObjectManager.Real import Real
from ...pyObjectManager.BitVec import BitVec
from ...pyObjectManager.String import String
from ...pyObjectManager.List import List
import logging
from ... import pyState
import itertools

logger = logging.getLogger("pyState:functions:zip")


def handle(state,call,left,right,ctx=None):
    """
    Simulate zip funcion
    """
    ctx = ctx if ctx is not None else state.ctx

    # Resolve the object
    lefts = state.resolveObject(left,ctx=ctx)

    # Normalize
    lefts = [lefts] if type(lefts) is not list else lefts

    # Resolve calls if we need to
    retObjs = [x for x in lefts if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs
    
    # Don't want to lose track of our vars
    lefts = [left.copy() for left in lefts]

    rights = state.resolveObject(right,ctx=ctx)

    # Normalize
    rights = [rights] if type(rights) is not list else rights

    # Resolve calls if we need to
    retObjs = [x for x in rights if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    rights = [right.copy() for right in rights]

    ret = []
    
    # Loop through possibilities
    for left,right in itertools.product(lefts,rights):

        # Only handling List and String objects for now
        if type(left) not in [List, String]:
            err = "handle: Don't know how to handle type {0}".format(type(left))
            logger.error(err)
            raise Exception(err)

        if type(right) not in [List, String]:
           err = "handle: Don't know how to handle type {0}".format(type(right))
           logger.error(err)
           raise Exception(err)

        # Create our output List
        newList = state.getVar('tmpZipList',ctx=1,varType=List)
        newList.increment()

        # Might as well use Python's own zip function to help us
        for (l,r) in zip(left,right):
           # TODO: This should really be a Tuple, but I haven't implemented that yet.
           tempList = state.getVar('tmpZipInner',ctx=1,varType=List)
           tempList.increment()
           tempList.variables = [l,r]
           newList.variables.append(tempList.copy())

        ret.append(newList.copy())

    return ret
