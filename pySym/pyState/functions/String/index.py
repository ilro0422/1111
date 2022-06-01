import logging
from ....pyObjectManager.List import List
from ....pyObjectManager.Int import Int
from ....pyObjectManager.Real import Real
from ....pyObjectManager.BitVec import BitVec
from ....pyObjectManager.Char import Char
from ....pyObjectManager.String import String
import ast

logger = logging.getLogger("pyState:SimFunction:String.index")


def handle(state,call,sub,start=None,end=None,ctx=None):
    """
    Determine location of char in string.
    """
    ctx = ctx if ctx is not None else state.ctx

    # The root (i.e.: "s" in s.index())
    root = state.resolveObject(call.func.value,ctx=ctx)

    assert len(root) == 1

    root = root.pop()

    assert type(root) is String

    # Resolve the vars
    subs = state.resolveObject(sub,ctx=ctx)

    for sub in subs:
        # If we're indexing a Char, just change it into a String
        if type(sub) is Char:
            c = sub
            sub = String("tempIndex",1,state=sub.state)
            sub.variables.append(c)
            subs[subs.index(c)] = sub

    
    assert min([type(sub) is String for sub in subs]) == True

    start = state.resolveObject(start,ctx=ctx) if start is not None else None
    end = state.resolveObject(end,ctx=ctx) if end is not None else None

    if type(start) not in [int,type(None)]:
        if not start.isStatic():
            err = "handle: Don't know how to handle appending type {0}".format(type(var))
            logger.error(err)
            raise Exception(err)
        start = start.getValue()

    if type(end) not in [int,type(None)]:
        if not end.isStatic():
            err = "handle: Don't know how to handle appending type {0}".format(type(var))
            logger.error(err)
            raise Exception(err)
        end = end.getValue()

    # Get the substring
    if start is None:
        start = 0
    
    if end is None:
        end = len(root)
    
    subStr = root[start:end]
    ret = []

    # Move the size window through the input
    for i in range(0,len(subStr) - len(sub) + 1):
        # If it is possible to have this index here, add it
        if subStr[i:i+len(sub)].canBe(sub):
            ret.append(Int('tempStrIndex',1,value=i,state=state))
        
        # If this is the only possible place, we must stop
        if subStr[i:i+len(sub)].mustBe(sub):
            break

    return ret


