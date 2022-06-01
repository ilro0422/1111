import z3
import weakref
from .. import pyState
from . import decorators

import logging
logger = logging.getLogger("ObjectManager:BitVec")

import os

class BitVec:
    """
    Define a BitVec
    """

    __slots__ = ['_clone', 'count', 'varName', 'ctx', 'size', 'value', 'uuid',
                 '__state', '__weakref__', 'parent']
    
    def __init__(self,varName,ctx,size,count=None,state=None,increment=False,value=None,uuid=None,clone=None):
        assert type(varName) is str
        assert type(ctx) is int
        assert type(size) is int

        self._clone = clone
        self.count = 0 if count is None else count
        self.varName = varName
        self.ctx = ctx
        self.size = size
        self.value = value
        self.uuid = os.urandom(32) if uuid is None else uuid
        self.parent = None
        self.state = state

        if increment:
            self.increment()

    def __deepcopy__(self,_):
        return self.copy()

    def __copy__(self):
        return self.copy()

    def copy(self):
        return BitVec(
            varName = self.varName,
            ctx = self.ctx,
            size = self.size,
            count = self.count,
            state = self.state if hasattr(self,"state") else None,
            value = self.value,
            uuid = self.uuid,
            clone = self._clone.copy() if self._clone is not None else None
        )

    def increment(self):
        """
        Increment the counter
        """
        self._clone = None
        self.value = None
        self.count += 1
        self.uuid = os.urandom(32)
        
    @decorators.as_clone
    def getZ3Object(self):
        """
        Returns the z3 object for this variable
        """
        
        # If we're not static    
        if self.value == None:
            return z3.BitVec("{0}{1}@{2}".format(self.count,self.varName,self.ctx),self.size,ctx=self.state.solver.ctx)

        return z3.BitVecVal(self.value,self.size)
    
    def _isSame(self,size):
        """
        Checks if variables for this object are the same as those entered.
        Assumes checks of type will be done prior to calling.
        """
        assert type(size) is int
        return True if size == self.size else False


    def setTo(self,var,*args,**kwargs):
        """
        Sets this BitVec object to be equal/copy of another. Type can be int, or BitVec
        """
        assert type(var) in [int, BitVec, Int], "Unhandled BitVec setTo type of {}".format(type(var))

        # Normalize Int to int if it's static, error otherwise
        if type(var) is Int:
            
            if var.isStatic():
                var = var.getValue()
            
            else:
                error = "Not handling symbolic Int value in setTo right now."
                logger.error(error)
                raise Exception(error)

        # Add the constraints

        # If we're not in the solver, we can play some tricks to make things faster
        #if not pyState.z3Helpers.varIsUsedInSolver(self.getZ3Object(),self.state.solver):
        if not self.state.var_in_solver(self.getZ3Object()):

            # Intentionally trying to unclutter the z3 solver here.
            if type(var) is int:
                self._clone = None
                self.value = var
                return

            elif var.isStatic():
                self._clone = None
                self.value = var.getValue()
                return

            elif type(var) is BitVec:
                logger.debug("BitVec {}: Setting clone to {}".format(self.varName, var.varName))
                self._clone = var
                return

        if type(var) is int:
            obj = var
        elif var.isStatic():
            obj = var.getValue()
        else:
            obj = var.getZ3Object()

        self.value = None
        self.state.addConstraint(self.getZ3Object() == obj)

    @decorators.as_clone
    def isStatic(self):
        """
        Returns True if this object is a static variety (i.e.: BitVecVal(12)).
        Also returns True if object has only one possibility
        """
        # If this is a static BitVec
        if self.value is not None:
            return True

        # If this is a BitVec with only one possibility
        if len(self.state.any_n_int(self,2)) == 1:
            return True

        return False

    @decorators.as_clone
    def getValue(self):
        """
        Resolves the value of this BitVec. Assumes that isStatic method is called
        before this is called to ensure the value is not symbolic
        """
        if self.value is not None:
            return self.value

        return self.state.any_int(self)

    @decorators.as_clone
    def __str__(self):
        """
        str will change this object into a possible representation by calling state.any_int
        """
        return str(self.getValue())

    @decorators.as_clone
    def __int__(self):
        return self.getValue()

    @decorators.as_clone
    def canBe(self,var):
        """
        Test if this BitVec can be equal to the given variable
        Returns True or False
        """
        if type(var) not in [Int, BitVec,int]:
            return False

        # Concrete answer
        if self.isStatic():
            if type(var) is int:
                return self.getValue() == var
            elif var.isStatic():
                var = var.getValue()
                if type(var) is str:
                    var = ord(var)
                assert type(var) is int
                return self.getValue() == var
        
        if type(var) in [Int, BitVec]:
            return self.state.isSat(extra_constraints=[self.getZ3Object() == var.getZ3Object()])

        else:
            return self.state.isSat(extra_constraints=[self.getZ3Object() == var])

    @decorators.as_clone
    def mustBe(self,var):
        """
        Test if this BitVec must be equal to another variable
        Returns True or False
        """

        # Concrete answer
        if self.isStatic():
            if type(var) is int:
                return self.getValue() == var
            elif var.isStatic():
                var = var.getValue()
                if type(var) is str:
                    var = ord(var)
                assert type(var) is int
                return self.getValue() == var

        if not self.canBe(var):
            return False

        # Can we be something else?
        if len(self.state.any_n_int(self,2)) == 2:
            return False

        # Ok, we can't be anything else. How about the var?
        if len(self.state.any_n_int(var,2)) == 2:
            return False

        # So we can be, now must we?
        #if len(self.state.any_n_int(self,2)) == 1:
        #    return True

        #return False
        # We CAN be the same, and neither of us can be different. We MUST be the same
        return True

    @property
    @decorators.as_clone_property
    def is_unconstrained(self):
        """bool: Returns True if this BitVec has no external constraints applied to it. False otherwise."""
        return not self.state.var_in_solver(self.getZ3Object())

    @property
    @decorators.as_clone_property
    def is_constrained(self):
        """bool: Opposite of is_unconstrained."""
        return not self.is_unconstrained

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

        # Pass to our clone
        if self._clone is not None:
            self._clone.state = state

from .Int import Int
from ..pyState import z3Helpers
