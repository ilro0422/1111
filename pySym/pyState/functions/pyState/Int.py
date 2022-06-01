
import z3
import ast
from ....pyObjectManager.Int import Int

def handle(state,call,ctx=None):
    """
    Returns an Int object. Use this to inform pySym that something should be Int symbolic
    """
    ctx = ctx if ctx is not None else state.ctx

    myInt = state.resolveObject(ast.Name('temp',0),ctx=1,varType=Int)

    # Everything is moved around as lists...
    for i in myInt:
        i.increment()

    return myInt.copy()
