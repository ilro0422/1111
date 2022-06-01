import ast
from copy import copy

def astCopy(self):
    new = self.__class__()

    #pypy has trouble writing to dict in this way :-(
    #new.__dict__ = {x: copy(getattr(self,x)) for x in self.__dict__}

    for attr in self.__dict__:
        setattr(new, attr, copy(getattr(self,attr)))

    return new


for t in ['If','While','Compare','Return','For', "Assign", "AugAssign","BinOp"]:
    getattr(ast,t).__copy__ = astCopy

def parse(s):
    """
    Parse string into python AST. Note that this needs to be separate due to hooking that I am performing on the objects.
    Returns: ast
    """
    return ast.parse(s)
