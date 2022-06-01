from ...pyObjectManager.List import List
from ...pyObjectManager.Int import Int
from ...pyObjectManager.BitVec import BitVec
import itertools
from ... import pyState
import logging

logger = logging.getLogger("pyState:functions:range")

def handle(state,call,a,b=None,c=None,ctx=None):
    """
    Simulate range funcion
    """
    ctx = ctx if ctx is not None else state.ctx

    # Resolve the vars
    aa = state.resolveObject(a,ctx=ctx)

    # Normalize
    aa = [aa] if type(aa) is not list else aa

    # Resolve calls if we need to
    retObjs = [x for x in aa if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    bb = state.resolveObject(b,ctx=ctx) if b is not None else None

    # Normalize
    bb = [bb] if type(bb) is not list else bb

    # Resolve calls if we need to
    retObjs = [x for x in bb if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    cc = state.resolveObject(c,ctx=ctx) if c is not None else None

    # Normalize
    cc = [cc] if type(cc) is not list else cc

    # Resolve calls if we need to
    retObjs = [x for x in cc if type(x) is pyState.ReturnObject]
    if len(retObjs) > 0:
        return retObjs

    ret = []

    # Loop through all possibilities
    for a,b,c in itertools.product(aa,bb,cc):

        ##############
        # a Concrete #
        ##############

        if type(a) not in [int,type(None)]:
            if a.isStatic():
                a = a.getValue()

            # Check if it's a variable that only has one possibility
            elif type(a) in [Int, BitVec] and len(state.any_n_int(a,2)) == 1:
                a = state.any_int(a)

            else:
                err = "handle: Don't know how to handle symbolic integers at the moment"
                logger.error(err)
                raise Exception(err)


        ##############
        # b Concrete #
        ##############
        if type(b) not in [int,type(None)]:
            if b.isStatic():
                b = b.getValue()

            # Check if it's a variable that only has one possibility
            elif type(b) in [Int, BitVec] and len(state.any_n_int(b,2)) == 1:
                b = state.any_int(b)
    
            else:
                err = "handle: Don't know how to handle symbolic integers at the moment"
                logger.error(err)
                raise Exception(err)
    

        ##############
        # c Concrete #
        ##############
    
        if type(c) not in [int,type(None)]:
            if c.isStatic():
                c = c.getValue()
    
            # Check if it's a variable that only has one possibility
            elif type(c) in [Int, BitVec] and len(state.any_n_int(c,2)) == 1:
                lower = state.any_int(c)
    
            else:
                err = "handle: Don't know how to handle symbolic integers at the moment"
                logger.error(err)
                raise Exception(err)
    
    
        # Create the return List object
        out = state.getVar("range",ctx=1,varType=List)
        out.increment()
    
        if b == None:
            rangeOut = range(a)
    
        elif c == None:
            rangeOut = range(a,b)
    
        else:
            rangeOut = range(a,b,c)
        
        # Copy the output
        for var in rangeOut:
            out.append(Int,kwargs={'value':var})
        
        # Return a copy
        ret.append(out.copy())
    
    return ret
        
