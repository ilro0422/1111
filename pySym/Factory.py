import logging
logger = logging.getLogger("Factory")

import ast
import enforce

from .pyPath import Path
from .pyPathGroup import PathGroup

#@enforce.runtime_validation
class Factory:

    __slots__ = ['__project','__weakref__']

    def __init__(self, project):
        self._project = project

    def path(self) -> Path:
        """pySym.pyPath.Path: Path object for this project."""

        # Read in the file
        with open(self._project.file_name, "r") as f:
            source = f.read()

        # Parse it
        body = ast.parse(source).body

        # Return the new path
        return Path(body,source=source,project=self._project)

    def path_group(self, *args, **kwargs) -> PathGroup:
        """pySym.pyPathGroup.PathGroup: Basic PathGroup object for this project."""
        kwargs['project'] = self._project
        return PathGroup(self.path(), *args, **kwargs)

    ##############
    # Properties #
    ##############

    @property
    def _project(self):
        """pySym.Project.Project: Associated Project object."""
        return self.__project

    @_project.setter
    def _project(self, project) -> None:
        if type(project) is not Project:
            raise Exception("Invalid type for project ({0}) should be type Project".format(type(project)))

        self.__project = project

from .Project import Project
