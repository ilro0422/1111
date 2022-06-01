import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, myPath + '/../')

import logging
from pySym import Colorer
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

from pySym import ast_parse
import z3
from pySym.pyPath import Path
from pySym.pyPathGroup import PathGroup
import pytest
from pySym.pyObjectManager.Int import Int
from pySym.pyObjectManager.Real import Real
from pySym.pyObjectManager.BitVec import BitVec
from pySym.pyObjectManager.List import List

test1 = """
l = zip([1,2,3],[4,5,6])
l1 = [1,2,3]
l2 = [4,5,6]
l3 = zip(l1,l2)
l4 = ["1","2","3"]
l5 = ["4","5","6"]
l6 = zip(l4,l5)
l7 = zip(["1","2","3","4"],["5","6"])
l8 = zip(["1","2"],["3","4","5","6"])
l9 = zip([1,2,3],"abc")
"""


def test_function_zip():
    b = ast_parse.parse(test1).body
    p = Path(b,source=test1)
    pg = PathGroup(p)

    pg.explore()
    assert len(pg.completed) == 1
    
    assert pg.completed[0].state.any_list('l') == [[1, 4], [2, 5], [3, 6]]
    assert pg.completed[0].state.any_list('l3') == [[1, 4], [2, 5], [3, 6]]
    assert pg.completed[0].state.any_list('l6') == [["1", "4"], ["2", "5"], ["3", "6"]]
    assert pg.completed[0].state.any_list('l7') == [["1","5"], ["2","6"]]
    assert pg.completed[0].state.any_list('l8') == [["1","3"], ["2","4"]] 
    assert pg.completed[0].state.any_list('l9') == [[1,"a"],[2,"b"],[3,"c"]]


