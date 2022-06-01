import z3
import ast
from ....pyObjectManager.Real import Real
from ... import z3Helpers

def handle(state,call,value=None,ctx=None):
    """
    Returns a z3 Real object. Use this to inform pySym that something should be Real symbolic
    (optional) value == the value to set this variable to
    """
    ctx = ctx if ctx is not None else state.ctx

    myReal = state.resolveObject(ast.Name('tempReal',0),ctx=ctx,varType=Real)
   
    ret = []

    for r in myReal:
 
        if value is not None:
            state = r.state
            value = state.resolveObject(value,ctx=ctx)

            for v in value:
                realObj,valueObj = z3Helpers.z3_matchLeftAndRight(r,v,ast.Add)
                #r.setTo(v)
                r.increment()
                state.addConstraint(r.getZ3Object() == valueObj)
                ret.append(r.copy())

        else:
            r.increment()
            ret.append(r.copy())

    return ret
