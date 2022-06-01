from ...pyObjectManager.Int import Int
from ...pyObjectManager.Real import Real
from ...pyObjectManager.BitVec import BitVec
from ...pyObjectManager.String import String
from ... import pyState
import logging

logger = logging.getLogger("pyState:functions:bin")


def handle(state,call,obj,ctx=None):
    """
    Simulate bin funcion
    """
    ctx = ctx if ctx is not None else state.ctx

    # Resolve the object
    objs = state.resolveObject(obj,ctx=ctx)
    
    # Normalize
    objs = [objs] if type(objs) is not list else objs

    # Resolve calls if we need to
    retObjs = [x for x in objs if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    retList = []

    # Loop through all possible inputs
    for obj in objs:

        if type(obj) not in [Int, Real, BitVec]:
            err = "handle: This shouldn't happen. Possibly a target program bug? Got obj type {0}".format(type(obj))
            logger.error(err)
            raise Exception(err)

        # Only dealing with concrete values for now.
        if obj.isStatic():
            val = obj.getValue()
            ret = state.getVar("tmpStrVal",ctx=1,varType=String)
            ret.increment()
            ret.setTo(bin(val),clear=True)
    
        # TODO: Deal with symbolic values (returning list of possibilities)
        else:
            err = "handle: Don't know how to handle symbolic ints for now"
            logger.error(err)
            raise Exception(err)


        retList.append(ret.copy())

    # Return all options
    return retList
