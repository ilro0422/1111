import logging
import z3
import ast
from .. import pyState
from . import Compare

logger = logging.getLogger("pyState:BoolOp")

def _handle(state,op,values,ifSideConstraints=None):
    ifSideConstraints = [] if ifSideConstraints is None else ifSideConstraints

    # Loop through our requested checks
    for value in values:
        if type(value) is ast.Compare:
            ifSide = Compare.handle(state,value)

            # Normalize
            ifSide = [ifSide] if type(ifSide) is not list else ifSide

            # Resolve calls if we need to
            retObjs = [x for x in ifSide if type(x) is pyState.ReturnObject]
            if len(retObjs) > 0:
                return retObjs


            # Recursively build this
            v = values[:]
            v.pop(0)
            ret = []
            for i in ifSide:
                ret += _handle(state,op,v,ifSideConstraints + [i])
            return ret

        else:
            err = "handle: Don't know how to handle type '{0}' at line {1} column {2}".format(type(value),value.lineno,value.col_offset)
            logger.error(err)
            raise Exception(err)

    # Change the checks into a Z3 Expression
    if type(op) is ast.And:
        ifSide = z3.And(ifSideConstraints)
        return [ifSide]

    elif type(op) is ast.Or:
        ifSide = z3.Or(ifSideConstraints)
        return [ifSide]

    else:
        err = "handle: Don't know how to handle op type '{0}' at line {1} column {2}".format(type(op),element.lineno,element.col_offset)
        logger.error(err)
        raise Exception(err)


def handle(state, element):
    """Attempt to handle the Python BoolOp element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.BoolOp
        element from source to be handled

    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast.

    
    This function handles calls to BoolOp. It is not meant to be called
    manually via a user.


    Example
    -------
    Example of ast.BoolOp is: x == 1 and y == 2
    """

    assert type(element) == ast.BoolOp
    
    op = element.op

    values = element.values
    
    return _handle(state,op,values)
