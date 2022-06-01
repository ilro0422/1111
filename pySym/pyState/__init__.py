import z3, z3.z3util as z3util
import ast
import logging
from copy import copy, deepcopy
import random
import os.path
import importlib
from types import ModuleType
import ntpath
import pickle
from ..pyObjectManager import ObjectManager
from ..pyObjectManager.Int import Int
from ..pyObjectManager.Real import Real
from ..pyObjectManager.BitVec import BitVec
from ..pyObjectManager.List import List
from ..pyObjectManager.Ctx import Ctx
from ..pyObjectManager.String import String
from ..pyObjectManager.Char import Char
from ..Project import Project

# Override z3 __copy__ so i can just use "copy()"
z3.z3.Solver.__copy__ = lambda self: self.translate(self.ctx)

# The current directory for running pySym
SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger("State")

_temporary_refs = set()

"""
def astCopy(self):
    new = self.__class__()
    newDict = {x: copy(getattr(self,x)) for x in self.__dict__}
    new.__dict__ = newDict
    return new

for t in ['If','While','Compare']:
    getattr(ast,t).__copy__ = astCopy
"""

# Create small class for keeping track of return values
class ReturnObject:

    __slots__ = ['retID', 'state']

    def __init__(self,retID,state=None):
        """Initialize a pySym.pyState.ReturnObject instance
    
        Parameters
        ----------
        retID : int
            Identification value for this ReturnObject
        state : pyState.State, optional
            State to associate this ReturnObject with


        Returns
        -------
        pySym.pyState.ReturnObject
    
        """
        self.retID = retID
        self.state = state
    
    def __deepcopy__(self,_):
        return ReturnObject(self.retID)

    def __copy__(self):
        return ReturnObject(self.retID)
    
    def copy(self):
        """Copies ReturnObject into an identical instance
        
        Returns
        -------
        pySym.pyState.ReturnObject
            ReturnObject with the same ID and State as the previous one
        """

        return ReturnObject(self.retID,self.state)

# I feel bad coding this but I can't find a better way atm.
def replaceObjectWithObject(haystack,fromObj,toObj,parent=None):
    """Generic search routine to replace an arbitrary object with another

    Parameters
    ----------
    haystack : any
        Where to search
    fromObj : any
        What to replace
    toObj : any
        What to replace with
    parent : any, optional
        (depreciated) What the parent object is. This option will be removed.


    Returns
    --------
    bool
        True/False if the object was successfully replaced.


    Find instance of fromObj in haystack and replace with toObj. This is used
    to ensure we know which function return is ours. Also now matches against
    lineno, col_offset and type. This will likely fail on polymorphic python code

    Example
    -------
    Replace the ast.Compare object with a Return object::

        In [1]: import ast

        In [2]: from pySym import pyState

        In [3]: ret = pySym.pyState.ReturnObject(5)

        In [4]: s = ast.parse("if 5 > 2:\\n\\tpass").body[0]

        In [5]: print(s.test)
        <_ast.Compare object at 0x7f563acb1b70>

        In [6]: assert pyState.replaceObjectWithObject(s,s.test,ret)

        In [7]: print(s.test)
        <pySym.pyState.ReturnObject object at 0x7f563b4c1048>

    """
    parent = haystack if parent is None else parent
    
    # If we found the object.
    if haystack == fromObj:
        parent[parent.index(fromObj)] = toObj
            
        return True
    
    # Gets a little tricky here finding our right index.. Lose matching
    if type(haystack) is type(fromObj) and haystack.lineno == fromObj.lineno and haystack.col_offset == fromObj.col_offset:
        index = [parent.index(x) for x in parent if type(x) is type(fromObj) and x.lineno is fromObj.lineno and x.col_offset is fromObj.col_offset]
        # Hopefully we only find one of these...
        assert len(index) == 1
        parent[index[0]] = toObj
        
        return True

    if type(haystack) == list:
        for x in haystack:
            if replaceObjectWithObject(x,fromObj,toObj,haystack):
                return True
    
    try:
        fields = haystack._fields
        if len(fields) == 0:
            return False
    except:
        return False

    for field in fields:
        if (getattr(haystack,field) == fromObj) or (type(getattr(haystack,field)) == type(fromObj) and getattr(haystack,field).lineno == fromObj.lineno and getattr(haystack,field).col_offset == fromObj.col_offset):
            setattr(haystack,field,toObj)
            return True

        if replaceObjectWithObject(getattr(haystack,field),fromObj,toObj,haystack):
            return True
    
    return False



def duplicateSort(obj):
    """
    Input:
        obj = z3 object to duplicate kind (i.e.: z3.IntSort()) --or--
              pyObjectManager type object (i.e.: Int)
    Action:
        Figure out details of the object and make duplicate sort
    Return:
        (class, kwargs)
        Duplicate pyObjectManager class object for this type (i.e.: Int)
    """

    args = {}

    # Resolve ast number objects to ObjectManager objects
    if type(obj) is ast.Num:
        if type(obj.n) is int:
            return Int, {'value': obj.n}
        return Real, {'value': obj.n}

    if type(obj) in [Int, Real, Char]:
        return type(obj), None

    if type(obj) is BitVec:
        return type(obj), {'size': obj.size}

    if type(obj) is String:
        # Create a string with the same length
        return type(obj), {'string': "A"*len(obj) if len(obj) > 0 else None}

    if type(obj) is List:
        return type(obj), None
    
    if type(obj) in [z3.IntNumRef,z3.RatNumRef,z3.ArithRef, z3.BitVecRef, z3.BitVecNumRef]:
        kind = obj.sort_kind()
     
    else:
        # Lookup Kind
        kind = obj.kind()
    
    kindTable = {
        z3.Z3_INT_SORT: Int,
        z3.Z3_REAL_SORT: Real,
        #z3.Z3_BOOL_SORT: z3.BoolSort()
    }
    
    if kind in kindTable:
        if type(obj) is z3.IntNumRef:
            args = {'value': obj.as_long()}
        return kindTable[kind], args

    #elif kind == z3.Z3_ARRAY_SORT:
    #    return z3.ArraySort(obj.domain().kind(),obj.range.kind())

    elif kind is z3.Z3_BV_SORT:
        return BitVec, {'size': obj.size()}
    
    else:
        err = "duplicateSort: unable to determine object sort '{0}'".format(obj)
        logger.error(err)
        raise Exception(err)



def get_all(f,rs=[]):
    """
    >>> x,y = Ints('x y')
    >>> a,b = Bools('a b')
    >>> get_all(Implies(And(x+y==0,x*2==10),Or(a,Implies(a,b==False))))
    [x, y, a, b]
    """
    if __debug__:
        assert z3util.is_expr(f), "Unexpected non-expression of type {}".format(type(f))

    if z3util.is_const(f):
        return z3util.vset(rs + [f],str)

    else:
        for f_ in f.children():
            rs = get_all(f_,rs)

        return z3util.vset(rs,str)

def hasRealComponent(expr):
    """Checks for Real component to a z3 expression
    
    Parameters
    ----------
    expr : z3 expression object


    Returns
    --------
    bool
        True if it has real componenet, False otherwise
        

    Checks if expression contains a real/non-int value or variable. This is
    genereally used in determining proper variable type to create. Z3 will cast
    Int to Real if you don't select the right type, which add extra complexity
    to the solving.


    Example
    -------
    Confirm that a Z3 expression has a Real component::

        In [1]: import z3

        In [2]: from pySym import pyState

        In [3]: r = z3.Real('r')

        In [4]: i = z3.Int('i')

        In [5]: pyState.hasRealComponent(r + i == 5)
        Out[5]: True

    """
    return max([False if type(x) not in [z3.ArithRef, z3.RatNumRef] else x.is_real() for x in get_all(expr)])


class State:
    """
    Defines the state of execution at any given point.
    """

    __slots__ = [
            'path', 'ctx', 'objectManager', 'solver', '__vars_in_solver',
            'functions', 'simFunctions', 'retVar', 'callStack', 'backtrace',
            'retID', 'loop', 'maxRetID', 'maxCtx', '__weakref__', '__project',
            ]

    def __init__(self,path=None,solver=None,ctx=None,functions=None,simFunctions=None,retVar=None,callStack=None,backtrace=None,retID=None,loop=None,maxRetID=None,maxCtx=None,objectManager=None,vars_in_solver=None,project=None):
        """
        (optional) path = list of sequential actions. Derived by ast.parse. Passed to state.
        (optional) backtrace = list of asts that happened before the current one
        (optional) vars_in_solver = dict of list of variable strings that are in the solver. Do not set this manually.
        (optional) project = pySym project file associated with this group. This will be auto-filled.
        """

        self._project = project
        self.path = [] if path is None else path
        self.ctx = 0 if ctx is None else ctx
        self.objectManager = objectManager if objectManager is not None else ObjectManager(state=self)
        self.solver = self.__new_solver() if solver is None else solver
        #self.solver.set("timeout", 60000) # 1 minute (in miliseconds) timeout for the solver
        self._vars_in_solver = vars_in_solver if vars_in_solver is not None else dict()
        self.functions = {} if functions is None else functions
        self.simFunctions = {} if simFunctions is None else simFunctions
        self.retVar = self.getVar('ret',ctx=1,varType=Int) if retVar is None else retVar
        self.callStack = [] if callStack is None else callStack
        self.backtrace = [] if backtrace is None else backtrace
        # Keep track of what our return ID is
        self.retID = retID
        self.loop = loop

        # Keeps track of what retIDs and Ctxs have been used
        self.maxRetID = 0 if maxRetID is None else maxRetID
        self.maxCtx = 1 if maxCtx is None else maxCtx
        
        # Initialize our known functions if this is the first time through
        if backtrace is None:
            self._init_simFunctions()

        # Make sure the state sticks around long enough to be used.
        global _temporary_refs
        _temporary_refs.add(self)

    def __new_solver(self):
        """Generates a new solver."""
        return z3.OrElse('smt', z3.Then("simplify","propagate-ineqs","propagate-values","unit-subsume-simplify","smt","fail-if-undecided"),z3.Then("simplify","propagate-ineqs","propagate-values","unit-subsume-simplify","qfnra-nlsat")).solver()


    def setVar(self,varName,var,ctx=None):
        """
        Convinence function that adds current ctx to setVar request
        """
        ctx = self.ctx if ctx is None else ctx
        return self.objectManager.setVar(varName=varName,ctx=ctx,var=var)

    def getVar(self,varName,ctx=None,varType=None,kwargs=None,softFail=None):
        """
        Convinence function that adds current ctx to getVar request
        """
        ctx = self.ctx if ctx is None else ctx
        return self.objectManager.getVar(varName,ctx,varType,kwargs,softFail=softFail)

    def recursiveCopy(self,var,ctx=None,varName=None):
        """
        Create a recursive copy of the given ObjectManager variable.
        This includes creating the relevant z3 constraints
        (optional) ctx = Context to copy in. Defaults to ctx 1 (RETURN_CONTEXT).
        (optional) varName = Specify what to name this variable
        Returns the copy
        """
        if type(var) is ReturnObject:
            return var

        assert type(var) in [Int, Real, BitVec, List, String, Char], "Unexpected var type of {}".format(type(var))
        assert type(varName) in [type(None), str], "Unexpected varName type of {}".format(type(varName))

        ctx = ctx if ctx is not None else 1
        varName = "tempRecursiveCopy" if varName is None else varName
        
        if type(var) in [Int, Real, BitVec, Char]:
            t, kwargs = duplicateSort(var)
            newVar = self.getVar(varName,ctx=ctx,varType=t,kwargs=kwargs)
            newVar.increment()
            # Add the constraints to the solver
            #self.addConstraint(var.getZ3Object() == newVar.getZ3Object())
            newVar.setTo(var)
            return newVar.copy()

        elif type(var) is List:
            newList = self.getVar(varName,ctx=ctx,varType=List)
            newList.increment()
            newList = newList.copy()
            # Recursively copy the list
            for elm in var:
                ret = self.recursiveCopy(elm,varName=varName)
                newList.append(ret)

            return newList

        elif type(var) is String:
            newString = self.getVar(varName,ctx=ctx,varType=String)
            newString.increment()
            newString = newString.copy()
            newString.setTo(var,clear=True)
            
            return newString
            

        # We shouldn't get here
        assert False
        
    def lineno(self):
        """
        Returns current line number. If returning from a call, returns the return line number
        Returns None if the program is done
        """
        
        # Return current lineno if exists
        if len(self.path) > 0:
            return self.path[0].lineno

        # Check if we're going back to the start of the loop
        if self.loop:
            return self.loop.body[0].lineno
        
        # Check up the call tree for instruction
        for cs in self.callStack[::-1]:
            if len(cs['path']) > 0:
                return cs['path'][0].lineno
            # If we're returning to start the loop anew
            if cs['loop']:
                return cs['loop'].lineno
        
        # Looks like we're done with the program
        return None
    

    def step(self):
        """
        Move the current path forward by one step
        Note, this actually makes a copy/s and returns them. The initial path isn't modified.
        Returns: A list of paths or empty list if the path is done 
        """
        global _temporary_refs

        # Adding sanity checks since we are not supposed to change during execution
        h = hash(self)

        # Optimize logger calls...
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug("step:\n\tpath = {0}\n\tcallStack = {1}\n\tctx = {2}\n\tretID = {3}\n\tsolver = {4}\n\tloop = {5}\n".format(self.path,self.callStack,self.ctx,self.retID,self.solver,self.loop))

        # More cleanly resolve instructions
        # TODO: Move this somewhere else... Moving it to the top of State introduced "include hell" :-(
        instructions = {
            ast.Assign: Assign,
            ast.AugAssign: AugAssign,
            ast.FunctionDef: FunctionDef,
            ast.Expr: Expr,
            ast.Pass: Pass,
            ast.Return: Return,
            ast.If: If,
            ast.While: While,
            ast.Break: Break,
            ast.For: For,
            ast.Assert: Assert,
            }

        # Return initial return state
        state = self.copy()
        
        # Check if we're out of instructions
        if len(state.path) == 0:
            # If we're in a loop, time to re-evaluate it
            if state.loop:
                state.path = [copy(state.loop)]
            # If we're not in a loop, try to pop up one on the stack
            elif not state.popCallStack():
                return []

        # Get the current instruction
        inst = state.path[0]

        # Check for hooks, give them the first shot at this
        if self._project is not None and inst.lineno in self._project._hooks:
            self._project._hooks[inst.lineno](state)

        # Generically handle any instruction we know about
        if type(inst) in instructions:
            ret_states = instructions[type(inst)].handle(state,inst)

        else:
            err = "step: Unhandled element of type {0} at Line {1} Col {2}".format(type(inst),inst.lineno,inst.col_offset)
            logger.error(err)
            raise Exception(err)

        # Move instruction to the done pile :-)
        for state in ret_states:
            state.backtrace.insert(0,inst)

        # Assert we haven't changed
        assert h == hash(self)

        # TODO: This will likely break if I implement multi-processing...
        # Clean up any temporary references
        _temporary_refs = set()
        
        # Return the paths
        return ret_states


    def Return(self,retElement):
        """
        Input:
            retElement = ast.Return element
        Action:
            Set return variable appropriately and remove the rest of the instructions in the queue
        Returns:
            Nothing for now
        """
        obj = retElement.value

        obj = self.resolveObject(obj)
        
        # Resolve calls if we need to
        retObjs = [x for x in obj if type(x) is ReturnObject]
        if len(retObjs) > 0:
            return retObjs

        logger.debug("Return: Returning element {1} = {0}".format(obj,self.retID))
        # Store it off in the objectManager
        self.objectManager.returnObjects[self.retID] = obj
        

        # Remove the remaining instructions in this function
        self.path = []


    def Call(self,call,func=None,retObj=None,ctx=None):
        """
        Input:
            call = ast.Call object
            (optional) func = resolved function for Call (i.e.: state.resolveCall(call)). This is here to remove duplicate calls to resolveCall from resolveObject
            (optional) ctx = Context to execute under. If left blank, new Context will be created.
        Action:
            Modify state in accordance w/ call
        Returns:
            ReturnObject the describes this functions return var
        """
        assert type(call) == ast.Call

        logger.debug("Call: Setting up for Call to {0}".format(call.func.id if type(call.func) is ast.Name else call.func.attr ))
        
        # Resolve the call
        func = self.resolveCall(call) if func is None else func
        logger.debug("Call: Resolved Function to {0}".format(func))
        
        # If the body is empty, don't actually call, just return []
        if len(func.body) == 0:
            logger.warn("Just made call to empty function {0}".format(funcName))
            return []
        
        if len(func.args.args) - len(func.args.defaults) > len(call.args):
            err = "call: number of arguments don't match expected, line {0} col {1}".format(call.lineno,call.col_offset)
            logger.error(err)
            raise Exception(err)

        
        # Grab a new context
        oldCtx = self.ctx

        if ctx is None:
            self.maxCtx += 1
            self.ctx = self.maxCtx
        else:
            self.ctx = ctx
        
        logger.debug("Call: Old CTX = {0} ... New CTX = {1}".format(oldCtx,self.ctx))
        
        ######################
        # Populate Variables #
        ######################
        # Create local vars dict
        if self.ctx not in self.objectManager.variables:
            self.objectManager.newCtx(self.ctx)

        # If there are arguments, fill them in
        for i in range(len(call.args)):
            caller_arg = self.resolveObject(call.args[i],ctx=oldCtx)
            caller_arg = [caller_arg] if type(caller_arg) is not list else caller_arg
            # Resolution should have already happened by pyState.Call.Handle
            assert len(caller_arg) == 1
            caller_arg = caller_arg.pop()
            varType, kwargs = duplicateSort(caller_arg)
            # We don't want static variables...
            kwargs.pop("value",None) if kwargs is not None else None
            #dest_arg = self.getVar(func.args.args[i].arg,varType=varType,kwargs=kwargs)
            #parent = self.objectManager.getParent(dest_arg)
            #index = parent.index(dest_arg)
            self.objectManager.variables[self.ctx][func.args.args[i].arg] = self.recursiveCopy(caller_arg,varName=func.args.args[i].arg)
            logger.debug("Call: Setting argument {0} = {1}".format(type(self.objectManager.variables[self.ctx][func.args.args[i].arg]),type(caller_arg)))

        # Grab any unset vars
        unsetArgs = func.args.args[len(call.args):]

        # Handle any keyword vars
        for i in range(len(call.keywords)):
            # Make sure this is a valid keyword
            if call.keywords[i].arg not in [x.arg for x in unsetArgs]:
                err = "call: Attempting to set invalid keyword '{0}' line {1} col {2}".format(call.keywords[i].arg,call.keywords[i].arg.lineno,call.keywords[i].arg.col_offset)
                logger.error(err)
                raise Exception(err)
            # NOTE: Assuming only one resolve from this due to Call.py handling the resolutions..
            caller_arg = self.resolveObject(call.keywords[i].value,ctx=oldCtx)
            caller_arg = [caller_arg] if type(caller_arg) is not list else caller_arg
            assert len(caller_arg) == 1
            caller_arg = caller_arg.pop()
            #caller_arg = caller_arg.getZ3Object() if type(caller_arg) in [Int, Real, BitVec] else caller_arg
            varType, kwargs = duplicateSort(caller_arg)
            # We don't want static variables...
            kwargs.pop("value",None) if kwargs is not None else None
            dest_arg = self.getVar(call.keywords[i].arg,varType=varType,kwargs=kwargs)
            #self.addConstraint(dest_arg.getZ3Object(increment=True) == caller_arg.getZ3Object())
            dest_arg.increment()
            dest_arg.setTo(caller_arg)
            # Remove arg after it has been satisfied
            unsetArgs.remove([x for x in unsetArgs if x.arg == call.keywords[i].arg][0])
            logger.debug("Call: Setting keyword argument {0} = {1}".format(type(dest_arg),type(caller_arg)))

        # Handle any defaults
        for arg in unsetArgs:
            argIndex = func.args.args.index(arg) - (len(func.args.args) - len(func.args.defaults))
            caller_arg = self.resolveObject(func.args.defaults[argIndex],ctx=oldCtx)
            caller_arg = [caller_arg] if type(caller_arg) is not list else caller_arg
            assert len(caller_arg) == 1
            caller_arg = caller_arg.pop()
            #caller_arg = caller_arg.getZ3Object() if type(caller_arg) in [Int, Real, BitVec] else caller_arg
            varType, kwargs = duplicateSort(caller_arg)
            # We don't want static variables...
            kwargs.pop("value",None) if kwargs is not None else None
            dest_arg = self.getVar(arg.arg,varType=varType,kwargs=kwargs)
            #self.addConstraint(dest_arg.getZ3Object(increment=True) == caller_arg.getZ3Object())
            dest_arg.increment()
            dest_arg.setTo(caller_arg)
            logger.debug("Call: Setting default argument {0} = {1}".format(type(dest_arg),type(caller_arg)))

       
        ####################
        # Setup Return Var #
        ####################
 
        # ctx of 1 is our return ctx
        # self.retVar = self.getZ3Var('ret',increment=True,varType=z3.IntSort(),ctx=1)
        # Generate random return ID
        oldRetID = self.retID
        self.retID = self.maxRetID + 1 # hash(call) # if retID is None else retID
        self.maxRetID += 1
        retObj = retObj if retObj is not None else ReturnObject(self.retID)
        # This isn't a duplicate call.. It's because I have to handle replacing the call function first using resolveObject..
        # TODO: Fire out better way than this.
        retObj.retID = self.retID
        retObj.state = self

        #################
        # Clearout Loop #
        #################
        # If we are calling something, save off our loop, but clear it out in current path
        oldLoop = self.loop
        self.loop = None
        
        ##################
        # Save CallStack #
        ##################
        cs = copy(self.path)
        if len(cs) > 0:
            self.pushCallStack(path=cs,ctx=oldCtx,retID=oldRetID,loop=oldLoop)
        
        self.path = func.body
        logger.debug("Call: Saved callstack: {0}".format(self.callStack))
        logger.debug("Call: Set new path {0}".format(self.path))
        
        # Return our ReturnObject
        return retObj

    ####################
    # Call Stack Stuff #
    ####################

    def pushCallStack(self,path=None,ctx=None,retID=None,loop=None):
        """
        Save the call stack with given variables
        Defaults to current variables if none given
        """
        self.callStack.append({
            'path': path if path is not None else self.path,
            'ctx': ctx if ctx is not None else self.ctx,
            'retID': retID if retID is not None else self.retID,
            'loop': loop if loop is not None else self.loop,
        })

    def popCallStack(self):
        """
        Input:
            Nothing
        Action:
            Pops from the call stack to the run stack. Adds call to completed state
        Returns:
            True if pop succeeded, False if there was nothing left to pop
        """

        # Check if we have somewhere to return to
        if len(self.callStack) == 0:
            return False

        # Pop the callStack back on to the run queue
        cs = self.callStack.pop()
        self.path = cs["path"]
        self.ctx = cs["ctx"]
        self.retID = cs["retID"]
        self.loop = cs["loop"]
        
        return True

    def copyCallStack(self):
        """
        Make a copy of the call stack, avoiding deepcopy
        Returns a copy of the current call stack
        """
        # TODO: Maybe make CallStack an Object/Class??

        ret = []

        # Loop through, copying each call stack
        for c in self.callStack:
            ret.append({
                'path': copy(c['path']),
                'ctx': c['ctx'],
                'retID': c['retID'],
                'loop': copy(c['loop'])
            })

        return ret
        

    ########################
    # End Call Stack Stuff #
    ########################
        

    def _init_simFunctions(self):
        """
        Input:
            Nothing
        Action:
            Initializes hooked functions (i.e.: pyState/functions/.)
        Returns:
            Nothing
        """
        # Base simFunction directory
        BASE = os.path.join(SCRIPTDIR,"functions")
        
        # Walk through functions
        for subdir, dirs, files in os.walk(BASE):
            if "__pycache__" in subdir:
                continue

            for f in files:
                if f in ['__init__.py'] or not f.endswith(('.py','.pyc','.pyo')):
                    continue

                # TODO: This is messy...
                modName = "." + os.path.join(subdir,f).replace(BASE,"").replace(f,"").strip("/").replace("/",".")
                modName = "" if modName is "." else modName
                modFName = os.path.splitext(f)[0]
                imp = importlib.import_module(('pySym.pyState.functions' + modName + "." + modFName).replace("..","."))
                self.registerFunction(imp,modName,True)


    def registerFunction(self,func,base=None,simFunction=None):
        """
        Input:
            func = ast func definition
            (optional) base = base path to import as (i.e.: "telnetlib" if importing "telnetlib.Telnet")
            (optional) simFunction = Boolean if this should be treated as a simFunction and therefore not handled symbolically. Defaults to False.
        Action:
            Register's this function as being known to this state
        Returns:
            Nothing
        """
        assert type(func) in [ast.FunctionDef,ModuleType]
        assert type(base) in [type(None),str]
        assert type(simFunction) in [type(None),bool]
        
        simFunction = False if simFunction is None else simFunction
        
        # Resolve the optional base
        base = "" if base is None else base
        # Add the end "." if needed
        base = base + "." if base is not "" and not base.endswith(".") else base
        
        # If this is a normal function
        if not simFunction:
            assert type(func) is ast.FunctionDef
            funcName = base + func.name
            logger.debug("registerFunction: Registering function '{0}'".format(funcName))
            self.functions[funcName] = func
        
        # This must be a simFunction
        else:
            assert type(func) is ModuleType
            funcName = func.__package__.replace("pySym.pyState.functions","") + "." + os.path.splitext(ntpath.basename(func.__file__))[0]
            funcName = funcName.lstrip(".")
            logger.debug("registerFunction: Registering simFunction '{0}'".format(funcName))
            self.simFunctions[funcName] = func

    def resolveCall(self,call,ctx=None):
        """
        Input:
            call = ast.Call object
            (optional) ctx = Context to resolve under
        Action:
            Determine correct ast.func object
        Returns:
            ast.func block
        """
        ctx = ctx if ctx is not None else self.ctx
        
        # If this is a local context call (i.e.: test())
        if type(call.func) == ast.Name:
            funcName = call.func.id
            logger.debug("resolveCall: Resolving call as name: %s", funcName)
        
        # If this is an attr form (i.e.: telnetlib.Telnet())
        elif type(call.func) == ast.Attribute:
            logger.debug("resolveCall: Resolving call as attribute call.")
            try:
                funcName = self.resolveObject(call.func.value,ctx=ctx)

                retObjs = [x for x in funcName if type(x) is ReturnObject]
                if len(retObjs) > 0:
                    return retObjs
                
                # NOTE: I'm assuming that if there are state splits, they will all be the same type
                # for instance, all String, all Char, all List, etc.
                funcName = funcName[0]
                
                funcName = funcName.__class__.__name__ + "." + call.func.attr

            except Exception as e:
                # TODO: Check exception type.. Don't just catch everything!
                funcName = call.func.value.id + "." + call.func.attr
                logger.debug("resolveCall: Resolved call name to '%s'", funcName)

        else:
                err = "resolveCall: unknown call-type object '{0}'".format(type(call))
                logger.error(err)
                raise Exception(err)

        # Give sim functions priority
        if funcName in self.simFunctions:
            return self.simFunctions[funcName]

        # If this function is a known local function, return it
        elif funcName in self.functions:
            return self.functions[funcName]

        else:
            err = "resolveCall: unable to resolve call to '{0}'".format(funcName)
            logger.error(err)
            raise Exception(err)


    def _resolveString(self,stringObject,ctx=None):
        """
        Input:
            stringObject = ast.List object
            (optional) ctx = Context of String to resolve. Default is current context
        Action:
            Resolve ast.String object into pyObjectManager.String.String object with Z3 constraints already added
        Returns:
            pyObjectManager.String.String object
        """
        assert type(stringObject) is ast.Str

        ctx = 1 if ctx is None else ctx
        
        # Get a temporary variable created
        newString = self.getVar('tmpResolveString',ctx=ctx,varType=String,kwargs={'string':stringObject.s})
        #newString = self.getVar('tmpResolveString',ctx=ctx,varType=String)
        #newString.increment()
        #newString.setTo(stringObject.s)
        
        return newString.copy()

    def _resolveList(self,listObject,ctx=None,i=0):
        """
        Input:
            listObject = ast.List object
            (optional) ctx = Context of List to resolve. Default is current context
        Action:
            Resolve ast.List object into pyObjectManager.List.List object
        Returns:
           List of  pyObjectManager.List.List object (i.e.: [List1, List2])
        """
        assert type(listObject) is ast.List

        ctx = self.ctx if ctx is None else ctx

        #############################
        # Resolve Calls in the list #
        #############################

        # Perform any calls if need be
        for elm in listObject.elts:
            if type(elm) is ast.Call:
                ret = self.resolveObject(elm)
                ret = ret if type(ret) is list else [ret]

                # If we're making a call, return for now so we can do that
                retObjs = [x for x in ret if type(x) is ReturnObject]
                if len(retObjs) > 0:
                    return retObjs


        ####################################
        # Append each element individually #
        ####################################
        varList = []
        # Create temporary variable if need be
        var = self.getVar('tempList{0}'.format(i),varType=List,ctx=1)
        # Make sure we get a fresh list variable
        var.increment()
   
        varList.append(var.copy())
 
        # TODO: This will probably fail on ReturnObjects
        for elm in listObject.elts:
            logger.debug("_resolveList: Adding {0} to tempList".format(elm))
            if type(elm) is ReturnObject:
                elm_resolved = self.resolveObject(elm)
                elm_resolved = [elm_resolved] if type(elm_resolved) is not list else elm_resolved

                newVarList = []

                for elm in elm_resolved:
                    t,args = duplicateSort(elm)
    
                    # Add this to all possible Lists
                    for var in varList:
                        if len(elm_resolved) > 1:
                            var = self.recursiveCopy(var)

                        var.append(var=t,kwargs=args)
                        if t in [Int, Real, BitVec]:
                            var[-1].setTo(elm)
                            #self.addConstraint(var[-1].getZ3Object() == elm.getZ3Object())
                        newVarList.append(var.copy())
                varList = newVarList

            elif type(elm) is ast.Num:
                elm_resolved = self.resolveObject(elm,ctx=ctx)
                elm_resolved = [elm_resolved] if type(elm_resolved) is not list else elm_resolved
                
                newVarList = []
                
                for elm in elm_resolved:
                    t, args = duplicateSort(elm)
                    
                    for var in varList:
                        if len(elm_resolved) > 1:
                            var = self.recursiveCopy(var)
                        var.append(t)
                        var[-1].setTo(elm)
                        #self.addConstraint(var[-1].getZ3Object() == elm.getZ3Object())
                        newVarList.append(var.copy())

                varList = newVarList
                 

            elif type(elm) is ast.List:
                # Recursively resolve this
                ret = self._resolveList(elm,ctx=ctx,i=i+1)
                ret = ret if type(ret) is list else [ret]

                # If we're making a call, return for now so we can do that
                retObjs = [x for x in ret if type(x) is ReturnObject]
                if len(retObjs) > 0:
                    return retObjs

                newVarList = []

                # For each List returned
                for elm in ret:

                    # For each List already existing
                    for var in varList:
                        # Only need a copy if we've got more than 1 returning
                        if len(ret) > 1:
                            var = self.recursiveCopy(var)
                        var.append(elm)
                        newVarList.append(var.copy())
                
                varList = newVarList

            elif type(elm) is ast.Str:
                elm_resolved = self.resolveObject(elm)
                for elm in elm_resolved:
                    # Append to every List
                    for var in varList:
                        var.append(elm.copy())
                

            elif type(elm) in [ast.Name, ast.BinOp]:
                # Resolve the name
                elm_resolved = self.resolveObject(elm)
                elm_resolved = elm_resolved if type(elm_resolved) is list else [elm_resolved]
                retObjs = [x for x in elm_resolved if type(x) is ReturnObject]
                if len(retObjs) > 0:
                    return retObjs

                newVarList = []
                # Loop through each returned element
                for elm in elm_resolved:

                    t,args = duplicateSort(elm)
                    
                    # Each List variable needs to get new objects
                    for var in varList:
                        # Optimization. If we only have one element, we don't need multiple copies
                        if len(elm_resolved) > 1:
                            # Create a copy
                            var = self.recursiveCopy(var)
                        
                        # Add constraints
                        var.append(var=t,kwargs=args)
                        var[-1].setTo(elm)
                        #if pyState.z3Helpers.isZ3Object(elm):
                        #    self.addConstraint(var[-1].getZ3Object() == elm)
                        #elif type(elm) in [Int, Real, BitVec]:
                        #    self.addConstraint(var[-1].getZ3Object() == elm.getZ3Object())
                        
                        # Add to the new var List
                        newVarList.append(var.copy())
                
                # Set the var list
                varList = newVarList

            elif type(elm) is ast.Call:
                # Resolve the call
                elm_resolved = self.resolveObject(elm)

                elm_resolved = elm_resolved if type(elm_resolved) is list else [elm_resolved]

                # If we're waiting on a symbolic call, return
                #retObjs = [x for x in elm_resolved if type(x) is pySym.pyState.ReturnObject]
                retObjs = [x for x in elm_resolved if type(x) is ReturnObject]
                if len(retObjs) > 0:
                    return retObjs

                newVarList = []

                # Loop through each return element
                for elm in elm_resolved:

                    # Make sure each List gets updated
                    for var in varList:
                        if len(elm_resolved) > 1:
                            var = self.recursiveCopy(var)

                        # Append it to the list
                        var.append(elm)
                        newVarList.append(var.copy())
                # Update the var list
                varList = newVarList

 
            else:
                err = "_resolveList: Don't know how to handle type {0} at line {1} col {2}".format(type(elm),listObject.lineno,listObject.col_offset)
                logger.error(err)
                raise Exception(err)

        # Return the resolved List
        return varList


    def resolveObject(self,obj,parent=None,ctx=None,varType=None,kwargs=None):
        """
        Input:
            obj = Some ast object (i.e.: ast.Name, ast.Num, etc)
                special object "PYSYM_TYPE_RETVAL" (int) will resolve the
                last return value

            (optional) parent = parent node of obj. This is needed for resolving calls
            (optional) ctx = Context other than current to resolve in
            (optional) varType = Type of the var to resolve. Needed if resolving a var that doesn't exist yet
            (optional) kwargs = kwargs for the var, needed if resolving a var that doesn't exist yet
        Action:
            Resolve object into something that can be used in a constraint
        Return:
            Resolved object
                ast.Num == int (i.e.: 6)
                ast.Name == pyObjectManager object (Int, Real, BitVec, etc)
                ast.BinOp == z3 expression of BinOp (i.e.: x + y)

        """
        ctx = self.ctx if ctx is None else ctx
        t = type(obj)

        # If the object is already resolved, just return it
        if t in [Int, Real, BitVec, List, Ctx, String, Char]:
            return [obj]
        
        if t == ast.Name:
            logger.debug("resolveObject: Resolving object type var named {0}".format(obj.id))

            # Try resolving a variable that's already defined in the current ctx
            var = self.getVar(obj.id,ctx=ctx,varType=varType,kwargs=kwargs,softFail=True)

            # If we resolved it return it
            if var is not None:
                return [var]
            
            # If we failed to resolve this variable, python will look upwards in the call tree
            for call in self.callStack[::-1]:
                var = self.getVar(obj.id,ctx=call['ctx'],varType=varType,kwargs=kwargs,softFail=True)
                
                # Did we find it in this context?
                if var is not None:

                    # We need to clone it so we don't mess with the original
                    t, kwargs = duplicateSort(var)
                    cloned_var = self.getVar("varInParentCtx", ctx=ctx, varType=t, kwargs=kwargs)
                    cloned_var.increment()
                    cloned_var.setTo(var,clear=True)

                    return [cloned_var]
                    
            else:
                err = "resolveObject: Could not resolve object named {}".format(obj.id)
                logger.error(err)
                raise Exception(err)
                
            #return [self.getVar(obj.id,ctx=ctx,varType=varType,kwargs=kwargs)]
        
        elif t == ast.Num:
            logger.debug("resolveObject: Resolving object type Num: {0}".format(obj.n))
            # Resolve this to an objectManager class
            t,args = duplicateSort(obj)
            return [t('tmp',ctx=ctx,state=self,**args if args is not None else {})]
            # Return real val or int val
            #return z3.RealVal(obj.n) if type(obj.n) == float else z3.IntVal(obj.n)
        
        elif t == ast.List:
            logger.debug("resolveObject: Resolving object type list: {0}".format(obj))
            return self._resolveList(obj,ctx=ctx)
    
        elif t == ast.Str:
            logger.debug("resolveObject: Resolving object type str: {0}".format(obj.s))
            #return self.getVar('tmp',ctx=1,varType=String,kwargs={'string':obj.s})
            return [self._resolveString(obj,ctx=ctx)]
        
        elif t == ast.BinOp:
            logger.debug("resolveObject: Resolving object type BinOp")
            return BinOp.handle(self,obj,ctx=ctx)

        elif t == ast.Subscript:
            logger.debug("resolveObject: Resolving object type Subscript")
            return Subscript.handle(self,obj,ctx=ctx)

        elif t == ReturnObject:
            logger.debug("resolveObject: Resolving return type object with ID: ret{0}".format(obj.retID))
            # Sometimes we run into a situation where we need to return the retID...
            # TODO: This is weird and seems like a hack...
            if obj.retID not in self.objectManager.returnObjects:
                return [obj]
            rets = self.objectManager.returnObjects[obj.retID]
            # make sure the state is sync'd
            for ret in rets:
                ret.state = self
            return rets

        elif t == ast.ListComp:
            logger.debug("resolveObject: Resolving ListComprehension")
            return ListComp.handle(self,obj,ctx=ctx)

        elif t == ast.GeneratorExp:
            logger.debug("resolveObject: Resolving GeneratorExpression")
            return GeneratorExp.handle(self,obj,ctx=ctx)

        elif t == ast.Compare:
            logger.debug("resolveObject: Resolving Compare")
            return pyState.Compare.handle(self,obj,ctx=ctx)

        # Hack-ish solution to handle calls
        elif t == ast.Call:

            logger.debug("resolveObject: Resolving Call")

            # Let's see if this is a real or sim call
            func = self.resolveCall(obj,ctx=ctx)

            # I think this will only hapen if we're resolving a call in a call
            if type(func) is list:
                return func
            
            # If this is a simFunction
            if type(func) is ModuleType:
                # Simple pass it off to the handler, filling in args as appropriate
                return func.handle(self, obj, *obj.args,ctx=ctx)

            # If we get here, we're a normal symbolic function
            else:
                # Change our state, record the return object
                o = Call.handle(self,obj)
                return o
            

        elif t == ast.UnaryOp:
            # TODO: Not sure if there will be symbolic UnaryOp objects... This wouldn't work for those.
            logger.debug("resolveObject: Resolving UnaryOp type object")
            #return ast.literal_eval(obj)
            return UnaryOp.handle(self,obj,ctx=ctx)


        else:
            err = "resolveObject: unable to resolve object '{0}' of type {1} in CTX {2}".format(obj,type(obj),ctx)
            logger.error(err)
            raise Exception(err)

    def popConstraint(self):
        """
        Pop last added constraint
        This doesn't seem to work...
        """
        self.solver.pop()

    def remove_constraints(self, constraints):
        """Removes the given z3 constraints.

        Args:
            constraints (list): List of z3 constraints to remove from the solver.

        Returns:
            int: Returns how many constraints were actually removed.
        """

        # Make it a list if need be
        if type(constraints) not in [list, tuple]:
            constraints = [constraints]

        new_constraints = [assertion for assertion in self.solver.assertions() if assertion not in constraints]

        # If we have less, then we successfully removed at least one thing
        ret_code = len(self.solver.assertions()) - len(new_constraints)

        # Removing is costly. Don't rebuild solver if we don't have to.
        if ret_code == 0:
            return 0

        self.solver = self.__new_solver()
        self.addConstraint(*new_constraints)

        # Remove the vars from our set tracker
        for constraint in constraints:
            if type(constraint) is bool:
                continue

            for var in set(get_all(constraint)):
                if type(var) not in [z3.z3.IntNumRef, z3.z3.BitVecNumRef]:
                    var = str(var)

                    if var in self._vars_in_solver:
                        try:
                            self._vars_in_solver[var].remove(str(constraint))
                            if self._vars_in_solver[var] == set():
                                self._vars_in_solver.pop(var)
                        except KeyError:
                            # Ignoring attempt to remove constraint that isn't tracked.
                            pass

        return ret_code


    def addConstraint(self,*constraints):
        """
        Input:
            constraints = Any number of z3 expressions to use as a constraint
        Action:
            Add constraint given
        Returns:
            Nothing
        """

        # Sanity checks
        for constraint in constraints:
            assert "z3." in str(type(constraint)) or type(constraint) is bool
        
        # No point in adding tautologies
        constraints = [constraint for constraint in constraints if type(constraint) is not bool or (type(constraint) is bool and constraint == False)]

        # If we're only adding True statements, ignore
        if constraints == []:
            return constraints

        # Add our new constraint to the solver
        self.solver.add(*constraints)

        # Record that they are now in the solver somewhere
        for constraint in constraints:

            if type(constraint) is bool:
                continue

            for var in set(get_all(constraint)):

                # Don't keep track of plain numbers. Only vars
                if type(var) not in [z3.z3.IntNumRef, z3.z3.BitVecNumRef]:
                    var = str(var)

                    # Init the dict if need be
                    if var not in self._vars_in_solver:
                        self._vars_in_solver[var] = set()
                        
                    self._vars_in_solver[var].add(str(constraint))


    def isSat(self,extra_constraints=None):
        """
        Input:
            extra_constraints: Optional list of extra constraints to temporarily add before checking for sat.
        Action:
            Checks if the current state is satisfiable
            Note, it uses the local and global vars to create the solver on the fly
        Returns:
            Boolean True or False
        """

        solver = self.solver

        if extra_constraints == None:
            return solver.check() == z3.sat

        if type(extra_constraints) not in [list, tuple]:
            extra_constraints = [extra_constraints]

        #
        # Deal with extra constraints
        #

        # Determine if we can push and pop
        try:
            solver.push()
            pushed = True
        except:
            pushed = False

        # Prefer push/pop
        if pushed:
            # Add in the constraints
            solver.add(*extra_constraints)
            ret = solver.check() == z3.sat
            # Pop off the constraints
            solver.pop()
            return ret

        # Use translate method
        else:
            solver = solver.translate(solver.ctx)
            solver.add(*extra_constraints)
            return solver.check() == z3.sat
        

    def printVars(self):
        """
        Input:
            Nothing
        Action:
            Resolves current constraints and prints viable variables
        Returns:
            Nothing
        """
        # Populate model
        if not self.isSat():
            print("State does not seem possible.")
            return
        
        # Set model
        m = self.solver.model()
        
        # Loop through model, printing out vars
        for var in m:
            print("{0} == {1}".format(var.name(),m[var]))


    def any_list(self,var,ctx=None):
        """
        Input:
            var == variable name. i.e.: "x"
            (optional) ctx = context if not current one
        Action:
            Resolve possible value for this variable (list)
        Return:
            Discovered variable or None if none found
        """
        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        # Solve model first
        if not self.isSat():
            logger.debug("any_list: No valid model found")
            # No valid ints
            return None

        if type(var) is not List:
            # Make sure the variable exists
            try:
                self.getVar(var,ctx=ctx)
            except:
                logger.debug("any_list: var '{0}' not found".format(var.varName))
                return None
    
            listObject = self.getVar(var,ctx=ctx)
   
        else:
            listObject = var
 
        if type(listObject) is not List:
            logger.warning("any_list: var '{0}' not of type List".format(var))
            return None
        
        out = []

        for elm in listObject:
            if type(elm) in [Int,BitVec]:
                out.append(self.any_int(elm,ctx=ctx))
            elif type(elm) is Real:
                out.append(self.any_real(elm,ctx=ctx))
            elif type(elm) is List:
                out.append(self.any_list(elm,ctx=ctx))
            elif type(elm) is Char:
                out.append(self.any_char(elm,ctx=ctx))
            elif type(elm) is String:
                out.append(self.any_str(elm,ctx=ctx))
            else:
                err = "any_list: unable to resolve object '{0}'".format(elm)
                logger.error(err)
                raise Exception(err)
        
        return out

    def any_n_int(self,var,n,ctx=None):
        """
        Input:
            var = variable name. i.e.: "x" --or-- ObjectManager object (i.e.: Int)
            n = number of viable solutions to find (i.e.: 5)
            (optional) ctx = context if not current one
        Action:
            Resolve n possible values for this variable
        Return:
            Discovered n values or [] if none found
        """
        # TODO: Optimize this... When slicing lists and needing, say, 256 values, this gets VERY slow... Silly..

        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        assert type(n) is int

        """
        # Doing this on a copy of the state since we're modifying it
        s = self.copy()
        #s = self

        varZ3Object = s.getVar(var,ctx=ctx).getZ3Object() if type(var) is str else var.getZ3Object()
        out = []

        for i in range(n):
            print("assertions",s.solver.assertions())
            #if len(s.solver.assertions()) == 2 and str(s.solver.assertions()[1]) == '010pyStateStringTemp[0]@1 != 1':
            #    assert False
            try:
                myInt = s.any_int(var,ctx=ctx)
            except:
                #Looks like we're done
                break

            if myInt == None:
                break
            
            out.append(myInt)
            s.addConstraint(varZ3Object != myInt)
            #solver.add(varZ3Object != myInt)

        print("Returning",out)
        return out

        """

        try:
            solver = self.solver
            solver.push()
            pushed = True
        except:
            pushed = False

        s = self
        varZ3Object = s.getVar(var,ctx=ctx).getZ3Object() if type(var) is str else var.getZ3Object()
        out = []

        #
        # Push method preferred
        #
        if pushed:
            logger.debug("any_n_int: Using push/pop method.")

            for i in range(n):

                try:
                    myInt = s.any_int(var,ctx=ctx)
                except:
                    #Looks like we're done
                    break

                if myInt == None:
                    break
                
                out.append(myInt)
                solver.add(varZ3Object != myInt)

            solver.pop()

        #
        # Fall back to other method TODO: Update this to use translate instead.
        # 

        else:
            logger.debug("any_n_int: Using legacy method.")

            extra_constraints = []

            for i in range(n):
                try:
                    myInt = s.any_int(var,ctx=ctx,extra_constraints=extra_constraints)
                except:
                    #Looks like we're done
                    break

                if myInt == None:
                    break
                
                out.append(myInt)
                extra_constraints.append(varZ3Object != myInt)

        return out

    def any_n_real(self,var,n,ctx=None):
        """
        Input:
            var = variable name. i.e.: "x" --or-- ObjectManager object (i.e.: Int)
            n = number of viable solutions to find (i.e.: 5)
            (optional) ctx = context if not current one
        Action:
            Resolve n possible values for this variable
        Return:
            Discovered possible values or [] if none found
        """
        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        assert type(n) is int

        # Doing this on a copy of the state since we're modifying it
        s = self.copy()

        varZ3Object = s.getVar(var,ctx=ctx).getZ3Object() if type(var) is str else var.getZ3Object()
        out = []

        for i in range(n):
            try:
                myInt = s.any_real(var,ctx=ctx)
            except:
                #Looks like we're done
                break

            if myInt == None:
                break

            out.append(myInt)
            s.addConstraint(varZ3Object != s.solver.model().eval(varZ3Object))

        return out


    """
    def any_n_str(self,var,n,ctx=None):
        Input:
            var = variable name. i.e.: "x" --or-- ObjectManager object (i.e.: String)
            n = number of viable solutions to find (i.e.: 5)
            (optional) ctx = context if not current one
        Action:
            Resolve n possible values for this variable
        Return:
            Discovered possible values or [] if none found
        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        assert type(n) is int

        # Doing this on a copy of the state since we're modifying it
        s = self.copy()

        varZ3Object = s.getVar(var,ctx=ctx).getZ3Object() if type(var) is str else var.getZ3Object()
        out = []

        for i in range(n):
            try:
                myInt = s.any_real(var,ctx=ctx)
            except:
                #Looks like we're done
                break

            if myInt == None:
                break

            out.append(myInt)
            s.addConstraint(varZ3Object != myInt)

        return out
    """


    def any_char(self,var,ctx=None):
        """
        Input:
            var == variable name. i.e.: "x" --or-- ObjectManager object (i.e.: Char)
            (optional) ctx = context if not current one
        Action:
            Resolve a possible value for this variable
        Return:
            Discovered variable or None if none found
        """
        assert type(var) in [str, Char]

        # Check if we have it in our variable
        if type(var) is str and self.getVar(var,ctx=ctx) == None:
            logger.debug("any_char: var '{0}' not in known variables".format(var))
            return None

        # Resolve the variable
        var = self.getVar(var,ctx=ctx) if type(var) is str else var

        # Solve model first
        if not self.isSat():
            logger.debug("any_char: No valid model found")
            return None

        # Get model
        m = self.solver.model()

        # Return a possible string
        #return chr(m.eval(var.getZ3Object(),model_completion=True).as_long())
        return chr(int(var))


    def any_str(self,var,ctx=None):
        """
        Input:
            var == variable name. i.e.: "x" --or-- ObjectManager object (i.e.: String)
            (optional) ctx = context if not current one
        Action:
            Resolve a possible value for this variable
        Return:
            Discovered variable or None if none found
        """
        assert type(var) in [str, String]

        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        # Solve model first
        if not self.isSat():
            logger.debug("any_str: No valid model found")
            return None

        # Get model
        m = self.solver.model()

        # Check if we have it in our variable
        if type(var) is str and self.getVar(var,ctx=ctx) == None:
            logger.debug("any_str: var '{0}' not in known variables".format(var))
            return None


        # Resolve the variable
        var = self.getVar(var,ctx=ctx) if type(var) is str else var
        
        # Return a possible string
        return ''.join([chr(m.eval(c.getZ3Object(),model_completion=True).as_long()) for c in var])
        


    def any_int(self,var,ctx=None, extra_constraints=None):
        """
        Input:
            var == variable name. i.e.: "x" --or-- ObjectManager object (i.e.: Int)
            (optional) ctx = context if not current one
            (optional) extra_constraints = tuple of extra constraints to temporarily place on the solve.
        Action:
            Resolve possible value for this variable
        Return:
            Discovered variable or None if none found
        """
        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        # Solve model first
        if not self.isSat():
            logger.debug("any_int: No valid model found")
            # No valid ints
            return None

        # If we're adding temporary constraints, create a temporary solver
        if extra_constraints is not None:
            # Normalize it to a tuple if need be
            if type(extra_constraints) not in [tuple, list]:
                extra_constraints = (extra_constraints,)

            # Try push/pop first
            try:
                solver = self.solver
                solver.push()
                pushed = True

            # Fall back to translate
            except:
                solver = self.solver.translate(self.solver.ctx)
                pushed = False

            solver.add(*extra_constraints)

            # Make sure this new situation is possible
            if solver.check() != z3.sat:
                if pushed:
                    solver.pop()
                return None

            m = solver.model()

            if pushed:
                solver.pop()
        
        else:
            m = self.solver.model()
        
        # Check if we have it in our localVars
        if type(var) is str and self.getVar(var,ctx=ctx) == None:
            logger.debug("any_int: var '{0}' not in known variables".format(var))
            return None

        var = self.getVar(var,ctx=ctx).getZ3Object() if type(var) is str else var.getZ3Object()
        
        # Try getting the value
        value = m.eval(var,model_completion=True)
        
        # Check if we have a known solution
        # Assuming local for now
        if type(value) == z3.ArithRef:
            logger.debug("any_int: var '{0}' not found in solution".format(var))
            # No known solution
            return None

        # Check the type of the value
        if type(value) not in [z3.IntNumRef,z3.BitVecNumRef]:
            err = "any_int: var '{0}' not of type int, of type '{1}'".format(var,type(value))
            logger.error(err)
            raise Exception(err)
        
        # Made it! Return it as an int
        return int(value.as_string(),10)

    """
    def any_num(self,var):
        Input:
            var == variable name. i.e.: "x"
        Action:
            Resolve possible value for this variable
        Return:
            Discovered variable or None if none found
            This will attempt to discover the correct type of variable (int/real) and return
            that type.
        
        # TODO: Do better than this... Check stuff first. Try/Catch isn't a great practice
        
        ret = None
        try:
            ret = self.any_int(var)
        except:
            pass
        
        if ret != None:
            return ret
        
        # Intentionally not catching exceptions here
        return self.any_real(var)
    """

    def any_real(self,var,ctx=None):
        """
        Input:
            var == variable name. i.e.: "x" --or-- ObjectManager Object (i.e.: Int)
            (optional) ctx = context if not current one
        Action:
            Resolve possible value for this variable
        Return:
            Discovered variable or None if none found
            Note: this function will cast an Int to a Real implicitly if found
        """
        # Grab appropriate ctx
        ctx = ctx if ctx is not None else self.ctx

        # Solve model first
        if not self.isSat():
            logger.debug("any_real: No valid model found")
            # No valid ints
            return None

        # Get model
        m = self.solver.model()

        if type(var) is str:
            try:
                self.getVar(var,ctx=ctx)
            except:
                logger.debug("any_real: var '{0}' not found".format(var))
                return None
        
        var = self.getVar(var,ctx=ctx).getZ3Object() if type(var) is str else var.getZ3Object()

        # Try getting the value
        value = m.eval(var,model_completion=True)

        # Check if we have a known solution
        # Assuming local for now
        if type(value) == z3.ArithRef:
            logger.debug("any_real: var '{0}' not found in solution".format(var))
            # No known solution
            return None

        # Check the type of the value
        if type(value) not in [z3.IntNumRef,z3.RatNumRef,z3.AlgebraicNumRef]:
            err = "any_real: var '{0}' not of type int or real, of type '{1}'".format(var,type(value))
            logger.error(err)
            raise Exception(err) 

        if type(value) is z3.AlgebraicNumRef:
            # Defaulting to precision of 10 for now
            return float(value.as_decimal(10).replace('?',''))

        # Made it! Return it as a real/float
        return float(eval(value.as_string()))

    def var_in_solver(self, var, ignore=None):
        """Checks if the variable given is in the z3 solver."""
        assert z3Helpers.isZ3Object(var), "Expected var to be z3 object, got type {} instead".format(type(var))
        var = str(var)
        
        # No constraints for this var
        if var not in self._vars_in_solver or self._vars_in_solver[var] is set():
            return False

        # If we're ignoring, do the filter
        if ignore is not None:

            # Standardize ignore
            if type(ignore) not in [list, tuple]:
                ignore = [ignore]

            ignore = [str(i) for i in ignore]
            constraints = set([constraint for constraint in self._vars_in_solver[var] if constraint not in ignore])

        else:
            constraints = self._vars_in_solver[var]

        return constraints != set()

    def copy(self):
        """
        Return a copy of the current state
        """

        # Copy the solver state
        #solverCopy = z3.Solver()
        #solverCopy = z3.OrElse(z3.Then("simplify","solve-eqs","smt","fail-if-undecided"),z3.Then("simplify","solve-eqs","nlsat")).solver()
        #solverCopy = z3.OrElse(z3.Then("simplify","propagate-ineqs","propagate-values","unit-subsume-simplify","smt","fail-if-undecided"),z3.Then("simplify","propagate-ineqs","propagate-values","unit-subsume-simplify","nlsat"),ctx=z3.Context()).solver()
        #solverCopy.add(self.solver.assertions())

        #solverCopy = self.solver.translate(self.solver.ctx)
        
        newState = State(
            #solver=solverCopy,
            solver=copy(self.solver),
            ctx=self.ctx,
            functions=self.functions,
            simFunctions=self.simFunctions,
            retVar=self.retVar,
            callStack=self.copyCallStack(),
            path=[copy(x) for x in self.path],
            backtrace=copy(self.backtrace),
            retID=copy(self.retID),
            loop=copy(self.loop),
            maxRetID=self.maxRetID,
            maxCtx=self.maxCtx,
            objectManager=self.objectManager.copy(),
            #vars_in_solver=deepcopy(self._vars_in_solver),
            vars_in_solver={key:copy(self._vars_in_solver[key]) for key in self._vars_in_solver.keys()},
            project=self._project
            )

        # Make sure to give the objectManager the new state
        newState.objectManager.state = newState

        return newState

    def __copy__(self):
        return self.copy()

    ##############
    # Properties #
    ##############

    @property
    def _vars_in_solver(self):
        """dict: Dict of sets of string representations of all the vars in the solver."""
        return self.__vars_in_solver

    @_vars_in_solver.setter
    def _vars_in_solver(self, vars):
        assert issubclass(type(vars), dict), "Unhandled _vars_in_solver type of {}".format(type(vars))

        self.__vars_in_solver = vars

    @property
    def _project(self):
        """pySym Project that this is associated with."""
        return self.__project

    @_project.setter
    def _project(self, project):
        assert isinstance(project, (Project, type(None))), "Invalid type for Project of {}".format(type(project))
        self.__project = project
        
from . import BinOp, Pass, While, Break, Subscript, For, ListComp, UnaryOp, GeneratorExp, Assign, AugAssign, FunctionDef, Expr, Return, If, Assert
from . import z3Helpers
