import z3
import weakref
import ast
import logging
from .. import pyState

logger = logging.getLogger("ObjectManager:List")

import os

class List:
    """
    Define a List
    """

    __slots__ = ['count', 'varName', 'ctx', 'variables', 'uuid', '__state', '__weakref__', 'variables_need_copy', 'parent']

    def __init__(self,varName,ctx,count=None,variables=None,state=None,increment=False,uuid=None):
        assert type(varName) is str
        assert type(ctx) is int

        self.count = 0 if count is None else count
        self.varName = varName
        self.ctx = ctx
        self.variables = [] if variables is None else variables
        self.variables_need_copy = [True] * len(self.variables)
        self.uuid = os.urandom(32) if uuid is None else uuid
        self.parent = None
        self.state = state

        if increment:
            self.increment()


    def copy(self):
        # Reset my copy requirements
        self.variables_need_copy = [True] * len(self.variables)

        return List(
            varName = self.varName,
            ctx = self.ctx,
            count = self.count,
            #variables = [x.copy() for x in self.variables],
            variables = self.variables,
            state = self.state if hasattr(self,"state") else None,
            uuid = self.uuid
        )

    def __deepcopy__(self,_):
        return self.copy()

    def __copy__(self):
        return self.copy()

    def __ensure_copy(self, index):
        """Small stub to ensure that we make a copy if we need to.
        
        index == Index to ensure will be a copy. If value is None, then perform full copy of list, not just index.
        """
        # If we're copying it all
        if index is None:
            self.variables = [copy(x) for x in self.variables]
            for var in self.variables:
                var.state = self.state
                var.parent = weakref.proxy(self)
            self.variables_need_copy = [False] * len(self.variables)

        # If this is the first touch, create a new list object for us
        else:
            if not any(val is False for val in self.variables_need_copy):
                self.variables = list(self.variables)

            # If we are in need of copy, do so
            if self.variables_need_copy[index] == True:
                self.variables[index] = copy(self.variables[index])
                self.variables[index].state = self.state # Pass it the correct state...
                self.variables[index].parent = weakref.proxy(self)
                self.variables_need_copy[index] = False


    def setTo(self,otherList,clear=False):
        """
        Sets this list to another of type List
        (optional) clear = Should we clear the current variables and set, or set the current variables in place retaining their constraints?
        """
        assert type(otherList) is List
        
        if clear:
            # Increment will also clear out the variables
            self.increment()
            
            # Just copy it over
            for elm in otherList:
                #self.variables.append(elm.copy())        
                #self.append(elm.copy())        
                self.append(elm)
        
        else:
            raise Exception("Not implemented")


    def increment(self):
        self.count += 1
        # reset variable list if we're incrementing our count
        self.variables = []
        self.variables_need_copy = []

        # Reset my copy requirements
        self.uuid = os.urandom(32)

        
    def append(self,var,kwargs=None):
        """
        Input:
            var = pyObjectManager oject to append (i.e.: Int/Real/etc)
            (optional) kwargs = optional keyword args needed to instantiate type
        Action:
            Resolves object, creates variable if needed
        Returns:
            Nothing
        """
        # Variable names in list are "<verson><varName>[<index>]". This is in addition to base naming conventions 

        self.__ensure_copy(None)

        if type(var) is Int or var is Int:
            logger.debug("append: adding Int")
            self.variables.append(Int('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state,**kwargs if kwargs is not None else {}))
            # We're being given an object. Let's make sure we link it to Z3 appropriately
            if type(var) is Int:
                self.variables[-1].setTo(copy(var))

        elif type(var) is Real or var is Real:
            logger.debug("append: adding Real")
            self.variables.append(Real('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state))
            if type(var) is Real:
                self.variables[-1].setTo(copy(var))

        elif type(var) is BitVec or var is BitVec:
            logger.debug("append: adding BitVec")
            kwargs = {'size': var.size} if kwargs is None else kwargs
            self.variables.append(BitVec('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state,**kwargs if kwargs is not None else {}))
            if type(var) is BitVec:
                self.variables[-1].setTo(copy(var))
        
        elif type(var) is Char or var is Char:
            logger.debug("append: adding Char")
            self.variables.append(Char('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state))
            if type(var) is Char:
                self.variables[-1].setTo(copy(var))

        elif type(var) in [List, String]:
            logger.debug("append: adding {0}".format(type(var)))
            self.variables.append(copy(var))

        else:
            err = "append: Don't know how to append/resolve object '{0}'".format(type(var))
            logger.error(err)
            raise Exception(err)

        self.variables_need_copy.append(True)


    def insert(self, index, object, kwargs=None):
        """Emulate the list insert method, just on this object."""

        assert type(index) in [int, Int], "Unexpected index of type {}".format(type(index))
        assert type(object) in [Int, Real, Char, BitVec, List, String], "Unexpected type for object of {}".format(type(object))

        self.__ensure_copy(None)

        # Use concrete int
        if type(index) is Int:
            assert index.isStatic(), "Insert got symbolic index value. Not supported."
            index = index.getValue()

        # Variable names in list are "<verson><varName>[<index>]". This is in addition to base naming conventions 
        
        logger.debug("insert: inserting {} at {}".format(type(object), index))

        if type(object) is Int:
            var = Int('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state,**kwargs if kwargs is not None else {})
            var.setTo(object)
            self.variables.insert(index, var)

        elif type(object) is Real:
            var = Real('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state)
            var.setTo(object)
            self.variables.insert(index, var)

        elif type(object) is BitVec:
            kwargs = {'size': object.size} if kwargs is None else kwargs
            var = BitVec('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state,**kwargs if kwargs is not None else {})
            var.setTo(object)
            self.variables.insert(index, var)
        
        elif type(object) is Char:
            var = Char('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state)
            var.setTo(object)
            self.variables.insert(index, var)

        elif type(object) in [List, String]:
            self.variables.insert(index, object)

        else:
            err = "append: Don't know how to append/resolve object '{0}'".format(type(var))
            logger.error(err)
            raise Exception(err)

        self.variables_need_copy.insert(index, True)


    def _isSame(self):
        """
        Checks if variables for this object are the same as those entered.
        Assumes checks of type will be done prior to calling.
        """
        return True

    def index(self,elm):
        """
        Returns index of the given element. Raises exception if it's not found
        """
        # Lookup our own variables by uuid
        if type(elm) in [String, Int, BitVec, Char, Real]:
            i = 0
            for var in self.variables:
                if var.uuid == elm.uuid:
                    return i
                i += 1
            raise Exception("Could not find object {}".format(elm))
            
        return self.variables.index(elm)

    def __getitem__(self,index):
        """
        We want to be able to do "list[x]", so we define this.
        """
        self.__ensure_copy(index)

        if type(index) is slice:
            # Build a new List object containing the sliced stuff
            newList = List("temp",ctx=self.ctx,state=self.state)
            oldList = self.variables[index]
            for var in oldList:
                newList.append(var.copy())
            return newList
            
        return self.variables[index]

    def __setitem__(self,key,value):
        """
        Sets value at index key. Checks for variable type, updates counter according, similar to getVar call
        """
        # Attempt to return variable
        assert type(key) is int
        assert type(value) in [Int, Real, BitVec, List, String]

        self.__ensure_copy(key)

        # Get that index's current count
        count = self.variables[key].count + 1

        if type(value) is Int:
            logger.debug("__setitem__: setting Int")
            self.variables[key] = Int('{2}{0}[{1}]'.format(self.varName,key,self.count),ctx=self.ctx,count=count,state=self.state)
            self.variables[key].setTo(value)

        elif type(value) is Real:
            logger.debug("__setitem__: setting Real")
            self.variables[key] = Real('{2}{0}[{1}]'.format(self.varName,key,self.count),ctx=self.ctx,count=count,state=self.state)
            self.variables[key].setTo(value)

        elif type(value) is BitVec:
            logger.debug("__setitem__: setting BitVec")
            self.variables[key] = BitVec('{2}{0}[{1}]'.format(self.varName,key,self.count),ctx=self.ctx,count=count,size=value.size,state=self.state)
            self.variables[key].setTo(value)

        elif type(value) in [List, String]:
            logger.debug("__setitem__: setting {0}".format(type(value)))
            self.variables[key] = value
            #value.count = count

        else:
            err = "__setitem__: Don't know how to set object '{0}'".format(value)
            logger.error(err)
            raise Exception(err)

        self.variables[key].parent = weakref.proxy(self)

    def pop(self,i):
        self.__ensure_copy(i)
        var = self.variables.pop(i)
        return var

    def mustBe(self,var):
        """
        Test if this List must be equal to another
        """
        if not self.canBe(var):
            return False

        # Check each item in turn to see if it must be
        for (item,val) in zip(self,var):
            if not item.mustBe(val):
                return False
        
        return True

    def canBe(self,var):
        """
        Test if this List can be equal to another List
        Returns True or False
        """
        if type(var) is not List:
            return False

        self.__ensure_copy(None)
        
        # If not the same length, we can't be the same
        if len(self) != len(var):
            return False
        
        # Compare pairwise Chars
        for (me,you) in zip(self,var):
            if not me.canBe(you):
                return False

        return True

    def __str__(self):
        self.__ensure_copy(None)
        return str(self.state.any_list(self))

    def __add__(self, other):
        self.__ensure_copy(None)
        assert type(other) is List, "Unsupported add of List and {}".format(type(other))

        # Build a new List to return
        new_list = List("tmpListAddList", ctx=self.ctx, state=self.state, increment=True)
        # Just set the variables directly
        #new_list.variables = self.variables + other.variables
        for var in self.variables + other.variables:
            new_list.append(var)

        return new_list

    def __len__(self):
        return len(self.variables)

    def getValue(self):
        """
        Return a possible value. You probably want to check isStatic before calling this.
        """
        self.__ensure_copy(None)
        return self.state.any_list(self)

    def isStatic(self):
        """
        Checks if this list can only have one possible value overall (including all elements).
        Returns True/False
        """
        self.__ensure_copy(None)
        # Check each of my items for static-ness
        for var in self:
            if not var.isStatic():
                return False

        return True

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


from copy import copy
# Circular importing problem. Don't hate :-)
from .Int import Int
from .Real import Real
from .BitVec import BitVec
from .Char import Char
from .String import String

