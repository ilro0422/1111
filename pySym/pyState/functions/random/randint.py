import logging
from ....pyObjectManager.Int import Int
from ....pyObjectManager import CTX_RETURNS
from .... import pyState
import z3

logger = logging.getLogger("pyState:functions:random.randint")


def handle(state,call,a,b,ctx=None):
    """
    Implements python random.randint
    """
    ctx = ctx if ctx is not None else state.ctx
    
    # Resolve arguments
    a_list = state.resolveObject(a,ctx=ctx)

    # If we're waiting on a symbolic call, return
    retObjs = [x for x in a_list if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    b_list = state.resolveObject(b,ctx=ctx)

    # If we're waiting on a symbolic call, return
    retObjs = [x for x in b_list if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    # Generally this will only be a single a and b value, but you never know.
    for a in a_list:

        # Not handling symbolic a rn
        if not a.isStatic():
            exc = "Not handling symbolic 'a' value in random.randint right now."
            logger.error(exc)
            raise Exception(exc)

        for b in b_list:
            
            # Not handling symbolic b rn
            if not b.isStatic():
                exc = "Not handling symbolic 'b' value in random.randint right now."
                logger.error(exc)
                raise Exception(exc)
            
            s = state.copy()
            
            # Create a new Int
            obj = s.getVar('tmpRandomRandint',ctx=CTX_RETURNS,varType=Int)

            # Add constraints
            s.addConstraint(z3.And(obj.getZ3Object() >= int(a), obj.getZ3Object() <= int(b)))

            # Done with this command
            #print(s.path.pop(0))

            ret.append(obj)

    return ret



