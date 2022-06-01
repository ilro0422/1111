import logging
logger = logging.getLogger("Project")
from . import Colorer

import enforce
import os
import types

#@enforce.runtime_validation
class Project:

    __slots__ = ['__file_name', '__factory', '__weakref__', '__hooks']

    def __init__(self, file, debug=False):
    
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        self.file_name = file
        self.factory = Factory(self)
        self._hooks = {}

    def hook(self, address, callback):
        """Registers pySym to hook address and call the callback when hit.

        Callback function will be called with the current state as the first parameter.

        Args:
            address (int): Line number of the source code to hook this callback to.
            callback (types.FunctionType): Function to call when line number is hit.

        Example:
            >>> def my_callback(state):
                    print(state)
            >>> project.hook(12, my_callback)
        """
        assert type(address) is int, "Unexpected address type of {}".format(type(address))
        assert type(callback) is types.FunctionType, "Unexpected callback type of {}".format(type(callback))

        # TODO: Sanity check that the number is within source range and that there's an instruction at that location
        self._hooks[address] = callback

    ##############
    # Properties #
    ##############

    @property
    def _hooks(self):
        """dict: Dictionary of registered hooks."""
        return self.__hooks

    @_hooks.setter
    def _hooks(self, hooks):
        assert isinstance(hooks, dict), "Unexpected type for hooks of {}".format(type(hooks))
        self.__hooks = hooks

    @property
    def factory(self):
        return self.__factory

    @factory.setter
    def factory(self, factory) -> None:
        self.__factory = factory

    @property
    def file_name(self) -> str:
        """str: Name of the file that's being symbolically executed."""
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: str) -> None:
        file_name = os.path.abspath(file_name)

        # Make sure this is a real file.
        if not os.path.isfile(file_name):
            raise Exception("Not a valid file: {file_name:s}".format(file_name=file_name))
        
        self.__file_name = file_name

from .Factory import Factory
