import z3
import weakref
import ast
import logging
from .. import pyState
from . import decorators

logger = logging.getLogger("ObjectManager:Char")

import os

class Char:
    """
    Define a Char (Character)
    """

    __slots__ = ['_clone', 'uuid', '__state', 'count', 'varName', 'ctx',
                 'variable', '__weakref__', 'parent']

    def __init__(self,varName,ctx,count=None,variable=None,state=None,increment=False,uuid=None,clone=None):
        assert type(varName) is str, "Unexpected varName type of {}".format(type(varName))
        assert type(ctx) is int, "Unexpected ctx type of {}".format(type(ctx))
        assert type(count) in [int, type(None)], "Unexpected count type of {}".format(type(count))

        self._clone = clone
        self.uuid = os.urandom(32) if uuid is None else uuid
        self.count = 0 if count is None else count
        self.varName = varName
        self.ctx = ctx
        self.variable = self.__make_variable(state) if variable is None else variable
        self.parent = None
        self.state = state

        if increment:
            self.increment()

    def __make_variable(self, state=None):
        if state == None:
            state = self.state
        return Int('{1}{0}'.format(self.varName,self.count),ctx=self.ctx,state=state)

    def __z3_bounds_constraint(self):
        """Returns the z3 bounds constraint for use in adding and removing it."""
        z3_obj = self.variable.getZ3Object() # This is hackish... But if I call my own getZ3Object it will recurse forever.
        return z3.And(z3_obj <= 0xff, z3_obj >= 0)

    def _add_variable_bounds(self):
        """Adds variable bounds to the solver for this Int to emulate a Char."""
        assert self.state is not None, "Char: Trying to add bounds without a state..."

        bounds = self.__z3_bounds_constraint()

        # If we're static, we don't need the bounds
        if self.isStatic():
            #if bounds in self.state.solver.assertions():
            self.state.remove_constraints(bounds)
            return

        # If we don't already have those added, add them
        if bounds not in self.state.solver.assertions():
            # We're ignoring these for the purpose of checking if the variable is in the solver. Sorta emulating a different var type.
            self.state.addConstraint(bounds)


    def __deepcopy__(self,_):
        return self.copy()

    def __copy__(self):
        return self.copy()

    def copy(self):
        return Char(
            varName = self.varName,
            ctx = self.ctx,
            count = self.count,
            variable = self.variable.copy(),
            state = self.state if hasattr(self,"state") else None,
            uuid = self.uuid,
            clone = self._clone
        )

    @decorators.as_clone
    def __str__(self):
        return chr(int(self))

    @decorators.as_clone
    def __int__(self):
        return ord(self.getValue())

    def setTo(self,var,*args,**kwargs):
        """
        Sets this Char to the variable. Raises exception on failure.
        """
        if type(var) not in [str, String, Char, Int]:
            err = "setTo: Invalid argument type {0}".format(type(var))
            logger.error(err)
            raise Exception(err)

        if (type(var) is String and len(var) != 1) or (type(var) is str and len(var) != 1):
            err = "setTo: Cannot set Char element to more than 1 length"
            logger.error(err)
            raise Exception(err)

        # We are becoming static
        if type(var) is str:
            self._clone = None
            # Remove our bounds constraints to help improve speed.
            self.state.remove_constraints(self.__z3_bounds_constraint())
            self.variable.setTo(ord(var))
        
        else:
            if type(var) is String:
                var = var[0]
            
            # Remove our bounds constraints to help improve speed.
            if var.isStatic():
                self._clone = None
                self.state.remove_constraints(self.__z3_bounds_constraint())
                self.variable.setTo(var)

            # We're being set to a non-static object
            else:

                # If we don't have any bounds ourselves, use clone approach
                if self.is_unconstrained and type(var) is Char:
                    self.state.remove_constraints(self.__z3_bounds_constraint())
                    self._clone = var.copy()

                else:
                    # Make sure we have our bounds set
                    self._add_variable_bounds()
                    self.variable.setTo(var)

    def increment(self):
        self._clone = None
        self.count += 1
        self.variable = self.__make_variable()
        self.uuid = os.urandom(32)
    
    def _isSame(self,**args):
        """
        Checks if variables for this object are the same as those entered.
        Assumes checks of type will be done prior to calling.
        """
        return True

    @decorators.as_clone
    def getZ3Object(self):
        # For now, adding Int bounds whenever our variable is accessed :-(
        self._add_variable_bounds()
        return self.variable.getZ3Object()

    @decorators.as_clone
    def isStatic(self):
        """
        Returns True if this object is a static variety (i.e.: "a").
        Also returns True if object has only one possibility
        """
        return self.variable.isStatic()

    @decorators.as_clone
    def getValue(self):
        """
        Resolves the value of this Char. Assumes that isStatic method is called
        before this is called to ensure the value is not symbolic
        """
        if self.isStatic():
            return chr(self.variable.getValue())

        return chr(self.state.any_int(self))

    @decorators.as_clone
    def mustBe(self,var):
        """
        Return True if this Char must be equivalent to input (str/Char). False otherwise.
        """
        assert type(var) in [str, Char]
        
        # If we can't be, then mustBe is also False
        if not self.canBe(var):
            return False
        
        # Utilize the BitVec's methods here
        if type(var) is str:
            return self.variable.mustBe(ord(var))

        if type(var) is Char:
            #return self.variable.mustBe(var.variable)        
            return self.variable.mustBe(var)

        # If we can be, determine if this is the only option
        #if len(self.state.any_n_int(self,2)) == 1 and len(self.state.any_n_int(var,2)) == 1:
        #    return True
        
        # Looks like we're only one option
        return False

    @decorators.as_clone
    def canBe(self,var):
        """
        Test if this Char can be equal to the given variable
        Returns True or False
        """

        assert type(var) in [str, Char]

        if type(var) is str and len(var) != 1:
            return False
        
        if type(var) is str:
            return self.variable.canBe(ord(var))

        elif type(var) is Char:
            #return self.variable.canBe(var.variable)
            return self.variable.canBe(var)

    @property
    @decorators.as_clone_property
    def is_unconstrained(self):
        """bool: Returns True if this Char has no external constraints applied to it. False otherwise."""
        
        # Consider it unconstrained if the only constraints are possibly the base ones that we have for Char
        #return not z3Helpers.varIsUsedInSolver(var=self.getZ3Object(),solver=self.state.solver,ignore=self.__z3_bounds_constraint())
        return not self.state.var_in_solver(self.getZ3Object(),ignore=self.__z3_bounds_constraint())

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

        # Turn it into a weakref
        if type(state) is pyState.State:
            self.__state = weakref.ref(state)

        # It's weakref or None. Set it
        else:
            self.__state = state

        self.variable.state = state
        
        if self._clone is not None:
            self._clone.state = state


# Circular importing problem. Don't hate :-)
from .BitVec import BitVec
from .Int import Int
from .String import String
from ..pyState import z3Helpers
