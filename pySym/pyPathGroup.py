import random
from multiprocessing import Pool
from .pyPath import Path
from .Project import Project

class PathGroup:

    __slots__ = ['active', 'deadended', 'completed', 'errored', 'found',
                 'ignore_groups', '__weakref__', '__search_strategy', '__project']

    def __init__(self, path=None, ignore_groups=None, search_strategy=None, project=None):
        """
        (optional) path = starting path object for path group
        (optional) discard_groups = List/set of path groups to ignore (i.e.: don't save) as we execute. Defaults to saving everything.
        (optional) search_strategy = Which paths to step? Valid: depth/breadth/random (default: breadth)
        (optional) project = pySym project file associated with this group. This will be auto-filled.
        """

        # Init the groups
        self.active = [path] if path is not None else []
        self.deadended = []
        self.completed = []
        self.errored = []
        self.found = []
        self.search_strategy = search_strategy
        self._project = project
        
        if ignore_groups is None:
            self.ignore_groups = set()
        elif type(ignore_groups) is str:
            self.ignore_groups = set([ignore_groups])
        elif type(ignore_groups) in [list, tuple]:
            self.ignore_groups = set(ignore_groups)
        else:
            raise Exception("Unsupported type of argument for ignore_groups of {}".format(type(ignore_groups)))


    def __str__(self):
        """
        Pretty print status
        """
        s = "<PathGroup with {0}>"

        # Figure out the attributes
        attr = []
        if len(self.active) > 0:
            attr.append("{0} active".format(len(self.active)))
        if len(self.deadended) > 0:
            attr.append("{0} deadended".format(len(self.deadended)))
        if len(self.completed) > 0:
            attr.append("{0} completed".format(len(self.completed)))
        if len(self.errored) > 0:
            attr.append("{0} errored".format(len(self.errored)))
        if len(self.found) > 0:
            attr.append("{0} found".format(len(self.found)))
        
        return s.format(', '.join(attr))

    def __repr__(self):
        return self.__str__()

    def explore(self,find=None):
        """
        Input:
            (optional) find = input line number to explore to
        Action:
            Step through script until line is found
        Returns:
            True if found, False if not
        """
        assert type(find) in [int,type(None)]
        
        while len(self.active) > 0:
            # Step the things
            self.step()

            if find:
                # Check for any path that has made it here
                for path in self.active:
                    if path.state.lineno() == find:
                        self.unstash(path,from_stash="active",to_stash="found")
                        return True


    def unstash(self,path=None,from_stash=None,to_stash=None):
        """
        Simply moving around paths for book keeping.
        """
        assert type(path) == Path
        assert type(from_stash) in [str, type(None)]
        assert type(to_stash) in [str, type(None)]

        if to_stash is not None and to_stash not in self.ignore_groups:
            to_stash = getattr(self,to_stash)
            to_stash.append(path)

        if from_stash is not None:
            from_stash = getattr(self,from_stash)
            from_stash.remove(path)


    def step(self):
        """
        Step all active paths one step.
        """
        #with Pool(processes=1) as pool:

        # Search Strategy
        if self.search_strategy == "breadth":
            paths = self.active
        elif self.search_strategy == "depth":
            paths = [self.active[-1]]
        # Random
        else:
            paths = random.sample(range(len(self.active)), random.randint(1,len(self.active)))
        
        for currentPath in paths:
            # It's possible this throws an exception on us
            try:
                paths_ret = currentPath.step()
                # Pop it off the block
                self.unstash(path=currentPath,from_stash="active")

            except Exception as e:
                currentPath.error = str(e)
                self.unstash(path=currentPath,from_stash="active",to_stash="errored")
                continue

            # If an empty list is returned, this path must be done
            if len(paths_ret) == 0:
                self.unstash(path=currentPath,to_stash="completed")
                continue
        
            # We have some return path
            else:
                for returnedPath in paths_ret:
                    # Make sure the returned path is possible
                    if not returnedPath.state.isSat():
                        self.unstash(path=returnedPath,to_stash="deadended")
                    else:
                        # We found our next step in the path
                        self.unstash(path=returnedPath,to_stash="active")

    @property
    def search_strategy(self):
        """str: Strategy for searching the paths.

        Valid options are:
           - Breadth (default): Traditional searching. Step each path in order.
           - Depth: Drill one path down as far as possible.
           - Random: Randomize what paths get stepped and what order.
        """
        return self.__search_strategy

    @search_strategy.setter
    def search_strategy(self, search_strategy):
        if search_strategy == None:
            search_strategy = "breadth"
        else:
            search_strategy = search_strategy.lower()
        assert search_strategy in ["breadth", "depth", "random"], "Search strategy '{}' is not valid.".format(search_strategy)
        self.__search_strategy = search_strategy

    @property
    def _project(self):
        """pySym Project that this is associated with."""
        return self.__project

    @_project.setter
    def _project(self, project):
        assert isinstance(project, (Project, type(None))), "Invalid type for Project of {}".format(type(project))
        self.__project = project
