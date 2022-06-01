import logging
logger = logging.getLogger("pyState:functions:pyState:BVV")

import z3
import ast
from ...z3Helpers import Z3_DEFAULT_BITVEC_SIZE
from ....pyObjectManager.BitVec import BitVec
from ....pyObjectManager.Int import Int
from .... import pyState

def _handle_num(i, size, ctx):
    """i is already resolved as Int or BitVec. size is not."""

    state = i.state.copy()

    # Resolve the size object
    size_vals = state.resolveObject(size,ctx=ctx)

    # Resolve calls if we need to
    retObjs = [x for x in size_vals if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    # Loop through sizes
    for size in size_vals:

        state = size.state.copy()

        if type(size) not in [Int, BitVec]:
            error = "Unhandled size type of {}".format(type(size))
            logger.error(error)
            raise Exception(error)

        assert size.isStatic(), "Not handling symbolic size value for pyState.BVV right now."

        # Resolve it to be an int
        size = size.getValue()

        # Generate a BitVec object for this.
        bvv = state.resolveObject(ast.Name('tempBVV',0),ctx=1,varType=BitVec,kwargs={'size': size})

        assert len(bvv) == 1, "pyState.BVV somehow resolved two values for ast.Num??"
        bvv = bvv.pop()

        bvv.increment()
        bvv.setTo(i)
        ret.append(bvv.copy())

    return ret

def handle(state,call,i,size=ast.Num(Z3_DEFAULT_BITVEC_SIZE),ctx=None):
    """
    Returns a BitVecVal object. This is helpful if we want to manually state what type a variable should be.
    """
    ctx = ctx if ctx is not None else state.ctx

    ret_bvv = []
    
    # Resolve the i object
    i_vals = state.resolveObject(i,ctx=ctx)

    # Resolve calls if we need to
    retObjs = [x for x in i_vals if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    # Loop through our possible i values
    for i in i_vals:

        if type(i) in [Int, BitVec]:
            ret_bvv += _handle_num(i, size, ctx)

        else:
            error = "Unhandled i type of {}".format(type(i))
            logger.error(i)
            raise Exception(i)

        # Resolve calls if we need to
        retObjs = [x for x in ret_bvv if type(x) is pyState.ReturnObject]
        if len(retObjs) > 0:
            return retObjs

    return ret_bvv

