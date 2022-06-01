
import z3
import ast
from ...z3Helpers import Z3_MAX_STRING_LENGTH
from ....pyObjectManager.String import String

def handle(state,call,length=ast.Num(Z3_MAX_STRING_LENGTH),ctx=None):
    """
    Returns a String object. This is helpful if we want to manually state what type a variable should be.
    Create a completely symbolic array of default max length:
        x = pyState.String()
    """
    ctx = ctx if ctx is not None else state.ctx

    assert type(length) in [ast.Num,int]
    length = length.n if type(length) is ast.Num else length
    
    string = state.getVar('pyStateStringTemp',ctx=1,varType=String,kwargs={'length': length})
    string.increment()

    return [string.copy()]
