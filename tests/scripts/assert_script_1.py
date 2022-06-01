def test():
    return 12

i = pyState.Int()
assert i % test() == 4
