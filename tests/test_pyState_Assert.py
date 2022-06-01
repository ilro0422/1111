import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))

import logging
from pySym import Colorer
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
from pySym.pyPathGroup import PathGroup
import pySym
import pytest

def test_assert_compare():
    proj = pySym.Project(os.path.join(myPath, "scripts", "assert_script_1.py"))
    pg = proj.factory.path_group()
    pg.explore()

    assert len(pg.completed) == 1
    s = pg.completed[0].state.copy()
    i = s.getVar('i')

    # Try some values
    assert all([x%12==4 for x in s.any_n_int(i, 32)])
