from ...pyObjectManager.Int import Int
from ... import pyState

def handle(state,call,obj,ctx=None):
    """
    Simulate len funcion
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

    # Loop through input

    ret = []
    
    for obj in objs:
    
        # Just calling the length function on the object..
        l = len(obj)
    
        i = state.getVar("tmpLenValue",ctx=1, varType=Int)
        i.increment()
    
        i.setTo(l)
    
        #ret.append(i.copy())
        ret.append(i)

    return ret
