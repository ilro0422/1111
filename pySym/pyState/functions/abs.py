from ...pyObjectManager.Int import Int
from ...pyObjectManager.Real import Real
from ...pyObjectManager.BitVec import BitVec
from ...pyObjectManager.String import String
from ... import pyState
import logging
import z3

logger = logging.getLogger("pyState:functions:abs")


def handle(state,call,obj,ctx=None):
    """
    Simulate abs funcion
    """
    ctx = ctx if ctx is not None else state.ctx

    # Resolve the object
    objs = state.resolveObject(obj,ctx=ctx)
    
    # Resolve calls if we need to
    retObjs = [x for x in objs if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    retList = []

    # Loop through all possible inputs
    for obj in objs:

        s = obj.state.copy()

        obj.state = s

        if type(obj) not in [Int, Real, BitVec]:
            err = "handle: This shouldn't happen. Possibly a target program bug? Got obj type {0}".format(type(obj))
            logger.error(err)
            raise Exception(err)
        
        oldObj = obj.copy()

        obj.increment()
        newObj = obj

        # Take shortcut if we know these values are static-ish
        if oldObj.isStatic():
            newObj.setTo(abs(oldObj.getValue()))

        else:

            # Add a little z3 If statement to mimic abs() call
            s.addConstraint(
                newObj.getZ3Object() == 
                z3.If(
                    oldObj.getZ3Object() > 0,
                    oldObj.getZ3Object(),
                    -oldObj.getZ3Object()
                    )
                )

        retList.append(obj.copy())

    # Return all options
    return retList
