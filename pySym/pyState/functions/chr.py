from ...pyObjectManager.Int import Int
from ...pyObjectManager.Real import Real
from ...pyObjectManager.BitVec import BitVec
from ...pyObjectManager.String import String
from ...pyObjectManager.List import List
import logging
from ... import pyState

logger = logging.getLogger("pyState:functions:chr")

import z3

def handle(state,call,obj,ctx=None):
    """
    Simulate chr funcion
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
        # TODO: Handle sending Exceptions back to the program, not us.
        if type(obj) is not Int:
            err = "handle: Invalid param for chr type {0}".format(type(obj))
            raise Exception(err)

        # Single value
        if obj.isStatic():

            # Is this integer too large or too small?
            obj_value = int(obj)
            if obj_value < 0 or obj_value >= 0x110000:
                err = "handle: Invalid integer value for chr of {0}. Needs to be in range(0x110000)".format(obj_value)
                raise Exception(err)

            # TODO: Figure out how to handle this case...
            elif obj_value > 0xff:
                err = "handle: Not sure how to handle chr(>0xff) right now..."
                raise Exception(err)


            # Grab a new var to work with
            ret = obj.state.getVar("tmpChrVal",ctx=1,varType=String,kwargs={'increment':True})
            ret.setTo(chr(int(obj)),clear=True)

        # If it's symbolic, we need help from z3
        else:
            # Grab a new var to work with
            ret = obj.state.getVar("tmpChrVal",ctx=1,varType=String,kwargs={'increment':True})
            ret.setTo(obj, clear=True)

        retList.append(ret.copy())

    return retList
