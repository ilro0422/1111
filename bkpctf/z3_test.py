#!/usr/bin/env python3

import pySym

proj = pySym.Project("./cipher_mod.py",debug=True)
pg = proj.factory.path_group()
pg.explore()

print("When z3 doesn't freeze, i should make it here in about 30 seconds. Otherwise, it will take infinite amount of time.")
