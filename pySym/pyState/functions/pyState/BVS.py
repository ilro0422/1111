import z3
import ast
from ...z3Helpers import Z3_DEFAULT_BITVEC_SIZE
from ....pyObjectManager.BitVec import BitVec

def handle(state,call,size=ast.Num(Z3_DEFAULT_BITVEC_SIZE),ctx=None):
    """
    Returns a BitVec object. Use this to inform pySym that something should be BitVec symbolic
    """
    ctx = ctx if ctx is not None else state.ctx

    assert type(size) is ast.Num, "Unknown size for BVS of type {}".format(type(size))

    bvs = state.resolveObject(ast.Name('temp',0),ctx=1,varType=BitVec,kwargs={'size': size.n})
    assert len(bvs) == 1

    bvs = bvs[0]
    bvs.increment()

    return [bvs.copy()]
