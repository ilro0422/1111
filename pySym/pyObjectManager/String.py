import z3
import weakref
import ast
import logging
from .. import pyState

logger = logging.getLogger("ObjectManager:String")

import os

class String:
    """
    Define a String
    """

    __slots__ = ['count', 'varName', 'ctx', 'variables', 'uuid', '__state', '__weakref__', 'parent']

    def __init__(self,varName,ctx,count=None,string=None,variables=None,state=None,length=None,increment=False,uuid=None):
        assert type(varName) is str
        assert type(ctx) is int
        assert type(count) in [int, type(None)]

        self.count = 0 if count is None else count
        self.varName = varName
        self.ctx = ctx
        # Treating string as a list of BitVecs
        self.variables = [] if variables is None else variables
        self.uuid = os.urandom(32) if uuid is None else uuid
        self.parent = None

        if increment:
            self.increment()

        self.state = state


        if string is not None:
            self.setTo(string,clear=True)

        # Add generic characters to this string
        if length is not None:
            for x in range(length):
                self._addChar()


    def copy(self):
        return String(
            varName = self.varName,
            ctx = self.ctx,
            count = self.count,
            variables = [x.copy() for x in self.variables],
            state = self.state if hasattr(self,"state") else None,
            uuid = self.uuid
        )

    def __deepcopy__(self, _):
        return self.copy()


    def __copy__(self):
        return self.copy()

    def increment(self):
        self.count += 1

        # increment all the chars
        for c in self:
            c.increment()

        self.uuid = os.urandom(32)
    
    def _addChar(self):
        """
        Append a generic Char item to this string.
        """
        self.variables.append(Char('{2}{0}[{1}]'.format(self.varName,len(self.variables),self.count),ctx=self.ctx,state=self.state))

    def setTo(self,var,clear=None):
        """
        Sets this String object to be equal/copy of another. Type can be str or String.
        clear = Boolean if this variable should be cleared before setting (default False)
        """
        assert type(var) in [String, Int, str], "Unhandled setTo type of {0}".format(type(var))
        
        clear = False if clear is None else clear
        
        if clear:
            self.variables = []

            # Hack to standardize how I treat the var.
            if type(var) is Int:
                var = [var]

            # For now, just add as many characters as there was originally
            for val in var:
                self._addChar()
                self[-1].setTo(val)
                """
                if type(val) is str:
                    #self.state.addConstraint(self[-1].getZ3Object() == ord(val))
                    self[-1].setTo(ord(val)
                else:
                    #self.state.addConstraint(self[-1].getZ3Object() == val.getZ3Object())
                    self[-1].setTo(val)
                """
        
        else:
            # Only set as much as we can.
            for (val,c) in zip(var,self):
                c.setTo(val)
                """
                if type(val) is str:
                    #self.state.addConstraint(c.getZ3Object() == ord(val))
                    c.setTo(ord(val))
                else:
                    #self.state.addConstraint(c.getZ3Object() == val.getZ3Object())
                    c.setTo(val)
                """

    def getZ3Object(self):
        """Convenience function. Will return z3 object for Chr if this is a string of length 1, else error."""

        if len(self) == 1:
            return self.variables[0].getZ3Object()

        raise Exception("String: getZ3Object with String of length {0} makes no sense.".format(len(self)))


    def _isSame(self,length=None,**args):
        """
        Checks if variables for this object are the same as those entered.
        Assumes checks of type will be done prior to calling.
        """
        if length is not len(self):
            return False
        return True

    def index(self,elm):
        """
        Returns index of the given element. Raises exception if it's not found
        """
        return self.variables.index(elm)

    def __getitem__(self,index):
        """
        We want to be able to do "string[x]", so we define this.
        """
        if type(index) is slice:
            # TODO: Redo this to return as string object
            # Build a new String object containing the sliced stuff
            # Create a copy
            newString = self.copy()

            # Adjust the variables down to the slice
            newString.variables = newString.variables[index]

            return newString
            

        return self.variables[index]

    def __setitem__(self,key,value):
        """
        String doesn't support setitem
        """
        err = "String type does not support item assignment"
        logger.error(err)
        raise Exception(err)

    def pop(self,index=None):
        """
        Not exactly something you can do on a string, but helpful for our symbolic execution
        """
        if index is not None:
            return self.variables.pop(index)
        else:
            return self.variables.pop()

    def __str__(self):
        """
        str will change this object into a possible representation by calling state.any_str
        """
        return self.state.any_str(self)

    def __len__(self):
        return len(self.variables)

    def mustBe(self,var):
        """
        Test if this string must be equal to the given variable. This means there's no other options and it's not symbolic
        """
        assert type(var) in [str, String]

        # TODO: Re-assess how i do this. Can probably make this more efficient...

        # If it's not even possible, just return no
        if not self.canBe(var):
            return False

        # If we can possible be this value, see if we MUST be this value
        # Loop through all our characters and see if they have more than one possibility
        for c in self:
            if len(self.state.any_n_int(c,2)) != 1:
                return False

        # Looks like we've got a match...
        return True

    def canBe(self,var):
        """
        Test if this string can be equal to the given variable
        Returns True or False
        """

        # May need to add String object canBe later
        assert type(var) in [str, String]
        
        # If we're dealing with a python string
        if type(var) is str:
            # It can't be equal if it's a different length...
            if len(self) != len(var):
                return False
            
            # Ask the solver...
            s = self.state.copy()
            for (me,you) in zip(self,var):
                # Add the constraint
                s.addConstraint(me.getZ3Object() == ord(you))
                # If we're not possible, return False
                if not s.isSat():
                    return False
        
            # If we made it here, it's a possibility
            return True
    
        # if we're dealing with a String object
        if type(var) is String:
            # It can't be equal if it's a different length...
            if len(self) != len(var):
                return False

            # Ask the solver...
            s = self.state.copy()
            for (me,you) in zip(self,var):
                # Add the constraint
                s.addConstraint(me.getZ3Object() == you.getZ3Object())
                # If we're not possible, return False
                if not s.isSat():
                    return False

            # If we made it here, it's a possibility
            return True

    def isStatic(self):
        """
        Returns True if this object is a static variety (i.e.: "test").
        Also returns True if object has only one possibility
        """
        # Check every character for multiple possible values
        for c in self:
            if not c.isStatic():
                return False

        # If all of them are static, this is a static string
        return True

    def getValue(self):
        """
        Resolves the value of this String. Assumes that isStatic method is called
        before this is called to ensure the value is not symbolic
        """
        return self.state.any_str(self)

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

        # Turn it into a weakref
        if type(state) is pyState.State:
            self.__state = weakref.ref(state)

        # It's weakref or None. Set it
        else:
            self.__state = state

        for var in self.variables:
            var.state = self.state

# Circular importing problem. Don't hate :-)
from .Int import Int
from .Real import Real
from .BitVec import BitVec
from .Char import Char

