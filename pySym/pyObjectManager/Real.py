import z3
import weakref
import logging
import os
from .. import pyState

logger = logging.getLogger("ObjectManager:Real")

class Real:
    """
    Define a Real
    """

    __slots__ = ['count', 'varName', 'ctx', 'value', 'uuid', '__state', '__weakref__', 'parent']
    
    def __init__(self,varName,ctx,count=None,value=None,state=None,increment=False,uuid=None):
        assert type(varName) is str
        assert type(ctx) is int
        assert type(value) in [type(None),float,int]

        self.count = 0 if count is None else count
        self.varName = varName
        self.ctx = ctx
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
        return Real(
            varName = self.varName,
            ctx = self.ctx,
            count = self.count,
            value = self.value,
            state = self.state if hasattr(self,"state") else None,
            uuid = self.uuid
        )

    def increment(self):
        self.value = None
        self.count += 1
        self.uuid = os.urandom(32)

    def getZ3Object(self,increment=False):
        """
        Returns the z3 object for this variable
        """
        
        if increment:
            self.increment()
        
        if self.value is None:
            return z3.Real("{0}{1}@{2}".format(self.count,self.varName,self.ctx),ctx=self.state.solver.ctx)

        return z3.RealVal(self.value)
    
    def _isSame(self,value=None):
        """
        Checks if variables for this object are the same as those entered.
        Assumes checks of type will be done prior to calling.
        """
        if value == self.value:
            return True
        return False

    def isStatic(self):
        """
        Returns True if this object is a static variety (i.e.: RealVal(12))
        """
        if self.value is not None:
            return True

        elif len(self.state.any_n_real(self,2)) == 1:
            return True

        return False

    def getValue(self):
        """
        Resolves the value of this real. Assumes that isStatic method is called
        before this is called to ensure the value is not symbolic
        """
        if self.value is not None:
            return self.value

        return self.state.any_real(self)

    def setTo(self,var,*args,**kwargs):
        """
        Sets this Real object to be equal/copy of another. Type can be float, Real, Int, or int
        """
        assert type(var) in [Real, float, Int, int]

        # Add the constraints

        # If we're not in the solver, we can play some tricks to make things faster
        #if not pyState.z3Helpers.varIsUsedInSolver(self.getZ3Object(),self.state.solver):
        if not self.state.var_in_solver(self.getZ3Object()):

            # If we're adding static, don't clutter up the solve
            if type(var) in [float, int]:
                self.value = var
                return

            elif var.isStatic():
                self.value = var.getValue()
                return

        if type(var) in [float, int]:
            obj = var
        elif var.isStatic():
            obj = var.getValue()
        else:
            obj = var.getZ3Object()

        # Be sure to reset our static value
        self.value = None

        self.state.addConstraint(self.getZ3Object() == obj)


    def __str__(self):
        """
        str will change this object into a possible representation by calling state.any_real
        """
        return str(self.state.any_real(self))

    def mustBe(self,var):
        """
        Test if this Real must be equal to another variable
        Returns True or False
        """
        if not self.canBe(var):
            return False

        # So we can be, now must we?
        #if len(self.state.any_n_real(self,2)) == 1:
        #    return True

        # Can we be something else?
        if len(self.state.any_n_int(self,2)) == 2:
            return False

        # Can the other var be something else?
        if len(self.state.any_n_int(var,2)) == 2:
            return False


        #return False
        return True


    def canBe(self,var):
        """
        Test if this Real can be equal to the given variable
        Returns True or False
        """
        # TODO: Maybe want canBe to include Integers?
        if type(var) not in [Real, float]:
            return False

        if type(var) is Real:
            return self.state.isSat(extra_constraints=[self.getZ3Object() == var.getZ3Object()])

        else:
            return self.state.isSat(extra_constraints=[self.getZ3Object() == var])

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


# Circular importing problem. Don't hate :-)
from .Int import Int
from .BitVec import BitVec

