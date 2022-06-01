import z3
import weakref
import ast
import logging
from .Int import Int
from .Real import Real
from .BitVec import BitVec
from .List import List
from .Ctx import Ctx
from .String import String
from .Char import Char
from .. import pyState

logger = logging.getLogger("ObjectManager")

CTX_GLOBAL = 0
CTX_RETURNS = 1

class ObjectManager:
    """
    Object Manager will keep track of objects. Generally, Objects will be variables such as ints, lists, strings, etc.
    """

    __slots__ = ['variables', 'returnObjects', '__state','__weakref__']

    def __init__(self,variables=None,returnObjects=None,state=None):
        self.variables = {CTX_GLOBAL: Ctx(CTX_GLOBAL), CTX_RETURNS: Ctx(CTX_RETURNS)} if variables is None else variables
        self.returnObjects = returnObjects if returnObjects is not None else {}

        if state is not None:
            self.state = state

    def newCtx(self,ctx):
        """
        Sets up a new context (ctx)
        """
        assert ctx is not None

        self.variables[ctx] = Ctx(ctx)
        self.variables[ctx].state = self.state

    def setVar(self,varName,ctx,var):
        """
        Input:
            varName = variable name (i.e.: 'x')
            ctx = Context to set for
            var = variable object of type pyObjectManager.X
        Action:
            Sets variable to the input (var) object
        Returns:
            Nothing
        """
        assert type(varName) is str
        assert type(ctx) is int
        assert type(var) in [Int, Real, BitVec, List]

        self.variables[ctx][varName] = var
        

    def getVar(self,varName,ctx,varType=None,kwargs=None,softFail=None):
        """
        Input:
            varName = name of variable to get
            ctx = Context for variable
            (optional) varType = Class type of variable (ex: pyObjectManager.Int)
            (optional) kwargs = args needed to instantiate variable
            (optional) softFail = True/False, should raise an exception if getVar fails. Default is False
        Action:
            Find appropriate variable object, creating one if necessary
        Returns:
            pyObjectManager object for given variable (i.e.: pyObjectManager.Int)
        """
        
        # Attempt to return variable
        assert type(varName) is str
        assert type(ctx) is int
        assert varType in [None, Int, Real, BitVec, List, String, Char]

        logger.debug("getVar: {} {} {} {}".format(varName,varType,kwargs,softFail))
        
        softFail = False if softFail is None else softFail
        create = False
        count = None
        
        # Check that we already have this variable defined
        if varName in self.variables[ctx]:
            
            # Check the type of the var is correct
            if varType is not None:

                # If the variable type is different or it's settings are different, we need to create a new object
                if type(self.variables[ctx][varName]) is not varType or not self.variables[ctx][varName]._isSame(**kwargs if kwargs is not None else {}):
                    create = True
                    # Re-using variable names is BAD!
                    count = self.variables[ctx][varName].count + 1
            
            # If we can just return the current one, let's do it
            if not create:
                return self.variables[ctx][varName]

        # Looks like we need to create a var
        if varType == None:
            if not softFail:
                err = "getVar: Need to create '{0}' but no type information given".format(varName)
                logger.error(err)
                raise Exception(err)
            else:
                # We're soft failing, just return None
                return None
        
        # Make the var
        self.variables[ctx][varName] = varType(varName=varName,ctx=ctx,count=count,state=self.state,**kwargs if kwargs is not None else {})
        
        return self.variables[ctx][varName]

    def getParent(self,key,haystack=None):
        """
        Returns the parent object for any given object by recursively searching.
        """

        """
        
        # Recursively resolve up the chain for JIT copy
        parents = [key, key.parent]
        while not isinstance(parents[-1], Ctx):
            parents.append[parents[-1].parent]

        # Now that we know the parents, start at the top and ensure JIT copy has happened for each step
        parents = parents[::-1]
        for i in range(len(parents)-1):
            parent = parents[i]
            child = parents[i+1]

            if isinstance(parent, (Ctx, List, String)):
                # Force JIT copy
                index = parent.index(child)
                parent[index]

            #elif isinstance(parent, Char):

        return key.parent
        """

        # TODO: This might get to be a long search if there are a lot of variables...

        #haystack = self.variables if haystack is None else haystack
        haystack = self.variables[key.state.ctx] if haystack is None else haystack

        if type(haystack) in [dict, Ctx]:
            for k,v in haystack.items():
                if hasattr(v,'uuid') and v.uuid == key.uuid:
                    return haystack
                elif type(v) in [dict, List, Ctx,String]:
                    p = self.getParent(key,v)
                    if p:
                        return p
        elif isinstance(haystack,(List,String)):
            for v in haystack:
                if hasattr(v,'uuid') and v.uuid == key.uuid:
                    return haystack
                elif type(v) in [dict,List,String]:
                    p = self.getParent(key,v)
                    if p:
                        return p
        elif isinstance(haystack,Char):
            if haystack.variable.uuid == key.uuid:
                return haystack


    def copy(self):
        """
        Return a copy of the Object Manager
        """

        return ObjectManager(
            variables = {key:self.variables[key].copy() for key in self.variables},
            returnObjects = {key:self.returnObjects[key].copy() for key in self.returnObjects},
        )

    def __copy__(self):
        return self.copy()

    @property
    def state(self):
        """Returns the state assigned to this object."""

        if self.__state is None:
            return None

        # Using weakref magic here
        return self.__state()

    @state.setter
    def state(self, state):
        assert type(state) in [pyState.State, weakref.ReferenceType, type(None)], "Unexpected state type of {}".format(type(state))

        # Turn it into a weakproxy
        if type(state) is pyState.State:
            self.__state = weakref.ref(state)

        else:
            self.__state = state

        for ctx in self.variables:
            self.variables[ctx].state = state
