import logging
from ....pyObjectManager.List import List
from ....pyObjectManager.Int import Int
from ....pyObjectManager.Real import Real
from ....pyObjectManager.BitVec import BitVec
from ....pyObjectManager.Char import Char
from ....pyObjectManager.String import String
import ast
from .... import pyState

logger = logging.getLogger("pyState:SimFunction:String.zfill")


def handle(state,call,width,ctx=None):
    """
    Simulate Python's zfill string method
    """
    ctx = ctx if ctx is not None else state.ctx

    # The root (i.e.: "s" in s.zfill())
    root = state.resolveObject(call.func.value,ctx=ctx)
    
    assert len(root) == 1
    root = root.pop()

    assert type(root) is String

    # Resolve the width
    widths = state.resolveObject(width,ctx=ctx)

    # Resolve calls if we need to
    retObjs = [x for x in widths if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    for width in widths:

        # TODO: Add symbolic width capability
        if not width.isStatic():
            err = "handle: Don't know how to handle non static width"
            logger.error(err)
            raise Exception(err)

        # TODO: Add symbolic string capability
        if not root.isStatic():
            err = "handle: Don't know how to handle symbolic string"
            logger.error(err)
            raise Exception(err)

        # Get new str
        newString = state.getVar('tempZfillStr',ctx=1,varType=String)
        newString.increment()
    
        # Resolve the width
        width = width.getValue()

        # zfill will not truncate
        newString.setTo(root,clear=True)
    
        # If we're already at our length, just return
        if len(newString) >= width:
            ret.append(newString.copy())
            continue

        # Add as many "0"s as needed
        while len(newString) < width:
            # Create the new Char
            c = state.getVar('tempCharZfill',ctx=1,varType=Char)
            c.increment()
            # Set it
            c.setTo('0')
            # Insert it
            newString.variables.insert(0,c.copy())

        ret.append(newString.copy())

    return ret

