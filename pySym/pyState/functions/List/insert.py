import logging
from ....pyObjectManager.List import List
from ....pyObjectManager.Int import Int
from ....pyObjectManager.Real import Real
from ....pyObjectManager.BitVec import BitVec
from ....pyObjectManager.String import String
from .... import pyState
from copy import copy

logger = logging.getLogger("pyState:SimFunction:List:insert")


def handle(state,call,index,object,ctx=None):
    """
    Insert object in a list at index
    """
    ctx = ctx if ctx is not None else state.ctx

    # Resolve index
    indexList = state.resolveObject(index,ctx=ctx)

    # If we're waiting on a symbolic call, return
    retObjs = [x for x in indexList if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs
    
    # Resolve what we're going to be inserting
    objList = state.resolveObject(object,ctx=ctx)

    # If we're waiting on a symbolic call, return
    retObjs = [x for x in objList if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    for obj in objList:

        for index in indexList:

            # Only static index for now
            if not index.isStatic():
                err = "List.insert called with symbolic index. This is not supported right now."
                logger.error(err)
                raise Exception(err)

            s = obj.state.copy()
            
            s.path.pop(0)

            # Resolve Root
            root = s.resolveObject(call.func.value,ctx=ctx)

            assert len(root) == 1, "Unhandled root of length {}".format(len(root))
            root = root.pop()

            assert type(root) is List, "Unexpected root type of {}".format(type(root))

            # Append it
            root.insert(index, copy(obj))
            
            # Add this to our returns
            retObj = pyState.ReturnObject(1)
            retObj.state = s

            ret.append(retObj)

    return ret



