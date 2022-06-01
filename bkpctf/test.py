#!/usr/bin/env python
def to_bits(length, N):
  #return [int(i) for i in bin(N)[2:].zfill(length)]
  out = []
  for i in range(length):
      out.insert(0, pyState.BVV((N >> i) & 1,1))
  return out

def from_bits(N):
  return int("".join(str(i) for i in N), 2)

CRC_POLY = to_bits(65, (2**64) + 0xeff67c77d13835f7)
CONST = to_bits(64, 0xabaddeadbeef1dea)

def crc(mesg):
  mesg += CONST
  shift = 0
  while shift < len(mesg) - 64:
    if mesg[shift]:
      for i in range(65):
        mesg[shift + i] ^= CRC_POLY[i]
    shift += 1
  return mesg[-64:]

INNER = to_bits(8, 0x36) * 8
OUTER = to_bits(8, 0x5c) * 8

"""
def xor(x, y):
  return [g ^ h for (g, h) in zip(x, y)]
"""

def xor(x, y):
  l = []
  for i in range(len(x)):
      l.append(x[i] ^ y[i])
  return l

"""
def hmac(h, key, mesg):
  return h(xor(key, OUTER) + h(xor(key, INNER) + mesg))
"""

def hmac(key, mesg):
  return crc(xor(key, OUTER) + crc(xor(key, INNER) + mesg))

PLAIN_1 = "zupe zecret"
PLAIN_2 = "BKPCTF"

def str_to_bits(s):
  return [b for i in s for b in to_bits(8, ord(i))]

def bits_to_hex(b):
  return hex(from_bits(b)).rstrip("L")
#
# Create key
#

KEY = []
for i in range(64):
    KEY.append(pyState.BVS(1))

#plain = str_to_bits(PLAIN_1)
p1 = hmac(KEY, str_to_bits(PLAIN_1))

# to_bits(64, 0xa57d43a032feb286) == [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0]

"""
if __name__ == "__main__":
  with open("key.txt") as f:
    KEY = to_bits(64, int(f.read().strip("\n"), 16))
  print PLAIN_1, "=>", bits_to_hex(hmac(crc, KEY, str_to_bits(PLAIN_1))) # Should equal 0xa57d43a032feb286
  print "BKPCTF{" + bits_to_hex(hmac(crc, KEY, str_to_bits(PLAIN_2))) + "}"
"""
