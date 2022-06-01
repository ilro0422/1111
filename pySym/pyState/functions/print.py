from ... import pyState

def handle(state,call,s,ctx=None):
    """
    Pretend to print stuff
    """
    ctx = ctx if ctx is not None else state.ctx

    s = state.resolveObject(s,ctx=ctx)
    
    # Resolve calls if we need to
    retObjs = [x for x in s if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    for obj in s:
        print(obj)
