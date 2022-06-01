import z3
import ast
import logging
from .pyState import State
from .Project import Project
from prettytable import PrettyTable
import sys
from copy import copy
from random import random

logger = logging.getLogger("Path")

class Path():
    """
    Defines a path of execution.
    """

    __slots__ = ['backtrace','state','source','error','__weakref__','__project']
    
    def __init__(self,path=None,backtrace=None,state=None,source=None,project=None):
        """
        (optional) path = list of sequential actions. Derived by ast.parse. Passed to state.
        (optional) backtrace = list of asts that happened before the current one
        (optional) state = State object for current path
        (optional) source = source code that we're looking at. This can make things prettier
        (optional) project = pySym project file associated with this group. This will be auto-filled.
        """
        
        self._project = project
        path = [] if path is None else path
        self.backtrace = [] if backtrace is None else backtrace
        self.state = State(path=path,project=self._project) if state is None else state
        self.source = source

    def step(self):
        """
        Move the current path forward by one step
        Note, this actually makes a copy/s and returns them. The initial path isn't modified.
        Returns: A list of paths or empty list if the path is done 
        """
        
        # Step-it
        stateList = self.state.step()
        
        pathList = []

        for state in stateList:
            # New path. State should already be copied via state.step above.
            path = self.copy(state=state)

            # New state
            #path.state = state

            pathList.append(path)

        return pathList
    
    def printBacktrace(self):
        """
        Convinence function to print out what we've executed so far
        """
        source = self.source
        source = source.split("\n") if source != None else None
        
        table = PrettyTable(header=False,border=False,field_names=["lineno","line","element"])
        table.align = 'l'
        
        for inst in self.state.backtrace[::-1]:
            table.add_row([
                "Line {0}".format(inst.lineno),
                source[inst.lineno-1] if source != None else " ",
                inst])
        
        print(table)
    
    def copy(self, state=None):
        """
        Input:
            (optional) state == pyState object to use instead of copying the current state.
        Action:
            Create a copy of the current Path object
        Returns:
            Copy of the path
        """
        # TODO: Don't think i need to copy state in this...
        return Path(
                backtrace=copy(self.backtrace),
                state=self.state.copy() if state is None else state,
                source=copy(self.source),
                project=self._project
                )

    def __copy__(self):
        return self.copy()

    @property
    def _project(self):
        """pySym Project that this is associated with."""
        return self.__project

    @_project.setter
    def _project(self, project):
        assert isinstance(project, (Project, type(None))), "Invalid type for Project of {}".format(type(project))
        self.__project = project
