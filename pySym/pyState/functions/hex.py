from ...pyObjectManager.Int import Int
from ...pyObjectManager.Real import Real
from ...pyObjectManager.BitVec import BitVec
from ...pyObjectManager.String import String
from ...pyObjectManager.List import List
import logging
from ... import pyState

logger = logging.getLogger("pyState:functions:hex")


def handle(state,call,obj,ctx=None):
    """
    Simulate hex funcion
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

    # Loop through our input
    retList = []

    for obj in objs:

        # This is probably a script problem, not us
        if type(obj) not in [Int, BitVec]:
            err = "handle: Invalid param for hex type {0}".format(type(obj))
            logger.error(err)
            raise Exception(err)

        # Only dealing with concrete values for now.
        if obj.isStatic():
            ret = state.getVar("tmpHexVal",ctx=1,varType=String)
            ret.increment()
            ret.setTo(hex(obj.getValue()),clear=True)

        # TODO: Deal with symbolic values (returning list of possibilities)
        else:
            err = "handle: Don't know how to handle symbolic for now"
            logger.error(err)
            raise Exception(err)


        retList.append(ret.copy())

    return retList
