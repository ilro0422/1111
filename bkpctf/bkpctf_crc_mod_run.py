#!/usr/bin/env python
from copy import copy
import z3
import pySym
import IPython

proj = pySym.Project("./bkpctf_crc_mod.py")

def hook_crc(state):
    shift = int(state.getVar('shift'))
    mesg = state.getVar('mesg')
    CRC_POLY = state.getVar('CRC_POLY', ctx=0)
    Then = []
    Else = []
    If = copy(mesg[shift]).getZ3Object() != 0

    print("Hit hook. Shift == " + str(shift))
    print("Len msg == " + str(len(mesg)))

    for i in range(65):
        old_c = copy(mesg[shift+i])
        new_c = mesg[shift+i]
        new_c.increment()
        Then.append(new_c.getZ3Object() == old_c.getZ3Object() ^ CRC_POLY[i].getZ3Object())
        Else.append(new_c.getZ3Object() == old_c.getZ3Object())

    state.addConstraint(z3.If(If, z3.And(Then), z3.And(Else)))
    mesg = state.getVar('mesg')[-64:]
    #print([c.state for c in mesg])
    #print(state)

def hook_interactive(state):
    IPython.embed()

proj.hook(21, hook_crc)
#proj.hook(64, hook_interactive)
pg = proj.factory.path_group(ignore_groups='deadended')

pg.explore()
