import pySym

proj = pySym.Project("./test_7.py")
pg = proj.factory.path_group()
pg.explore()
