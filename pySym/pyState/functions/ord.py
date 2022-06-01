from ...pyObjectManager.Int import Int
from ...pyObjectManager.Real import Real
from ...pyObjectManager.BitVec import BitVec
from ...pyObjectManager.String import String
from ...pyObjectManager.List import List
from ...pyObjectManager.Char import Char
import logging
from ... import pyState

logger = logging.getLogger("pyState:functions:ord")

import z3

def handle(state,call,obj,ctx=None):
    """
    Simulate ord funcion
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
        if (type(obj) not in [String, Char]) or (type(obj) is String and len(obj) != 1):
            err = "handle: Invalid param for ord type {0}".format(type(obj))
            logger.error(err)
            raise Exception(err)

        # Grab a new var to work with
        ret = state.getVar("tmpOrdVal",ctx=1,varType=Int)
        ret.increment()

        # Sanitize String to Char
        if type(obj) is String:
            obj = obj[0]

        # Simple case, it's static
        if obj.isStatic():
            ret.setTo(ord(obj.getValue()))

        # If it's symbolic, we need help from z3
        else:
            # Tell z3 to convert the BitVec to an int, then set equal
            #ret.state.addConstraint(z3.BV2Int(obj.getZ3Object()) == ret.getZ3Object())
            ret.setTo(obj)

        retList.append(ret.copy())

    return retList
