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

test = """
def to_bits(length, N):
  return [int(i) for i in bin(N)[2:].zfill(length)]

def from_bits(N):
  return int("".join(str(i) for i in N), 2)

CRC_POLY = to_bits(65, (2**64) + 0xeff67c77d13835f7) # 0b11110111111110110011111000111011111010001001110000011010111110111

def crc(mesg):
  mesg += CONST
  shift = 0
  while shift < len(mesg) - 64:
    if mesg[shift]:
      for i in range(65):
        mesg[shift + i] ^= CRC_POLY[i]
    shift += 1
  return mesg[-64:]

INNER = to_bits(8, 0x36) * 8 # 0b0011011000110110001101100011011000110110001101100011011000110110

def xor(x, y):
  return [g ^ h for (g, h) in zip(x, y)]

def hmac(h, key, mesg):
  return h(xor(key, OUTER) + h(xor(key, INNER) + mesg))

PLAIN_1 = "zupe zecret"
PLAIN_2 = "BKPCTF"

def str_to_bits(s):
  return [b for i in s for b in to_bits(8, ord(i))]

def bits_to_hex(b):
  return hex(from_bits(b)).rstrip("L")

PLAIN_1_BITS = str_to_bits(PLAIN_1)
"""

def test_longer_one():
    b = ast_parse.parse(test).body
    p = Path(b,source=test)
    pg = PathGroup(p)

    pg.explore()

    assert len(pg.completed) == 1

    assert pg.completed[0].state.any_list('CRC_POLY') == [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1]

    assert pg.completed[0].state.any_list('INNER') == [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0]

    assert pg.completed[0].state.any_list('PLAIN_1_BITS') == [0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0]

