import logging
import z3
import ast
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Real import Real
from ..pyObjectManager.BitVec import BitVec
from ..pyObjectManager.List import List
from .. import pyState
from . import ListComp

logger = logging.getLogger("pyState:GeneratorExp")

#import astunparse


def handle(state,element,ctx=None):
    """Attempt to handle the Python GeneratorExp element
    
    Parameters
    ----------
    state : pyState.State
        pyState.State object to handle this element under
    element : ast.GeneratorExp
        element from source to be handled


    Returns
    -------
    list
        list contains state objects either generated or discovered through
        handling this ast. 
    

    This function handles calls to ast.GeneratorExp. It is not meant to be
    called manually via a user. Under the hood, it converts the generator
    expression into a list comprehension and calls the handler for list
    comprehension.


    Example
    -------
    Example of ast.GeneratorExp is: x for x in [1,2,3] (note it's not inside
    List Comprehension brackets)
    """

    assert type(element) is ast.GeneratorExp

    ctx = state.ctx if ctx is None else ctx

    # NOTE: Maybe there are cases where we don't want the GeneratorExp to be turned into ListComp?

    # Create a skelleton ListComp
    listComp = ast.parse("[x for x in []]").body[0].value

    # Pop in our generator
    listComp.generators = element.generators
    
    # Pop in our element
    listComp.elt = element.elt

    # Make the switch
    pyState.replaceObjectWithObject(state.path[0],element,listComp)

    #print(astunparse.unparse(element))
    #print(astunparse.unparse(listComp))

    # Call ListComp to handle this
    return ListComp.handle(state,listComp,ctx=ctx)


