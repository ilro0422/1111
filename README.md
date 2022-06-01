# pySym
Python Symbolic Execution

[![Build Status](https://travis-ci.org/bannsec/pySym.svg?branch=master)](https://travis-ci.org/bannsec/pySym)
[![Coverage Status](https://coveralls.io/repos/github/Owlz/pySym/badge.svg?branch=HEAD)](https://coveralls.io/github/Owlz/pySym?branch=HEAD)
[![Documentation Status](https://readthedocs.org/projects/pysym/badge/?version=latest)](http://pysym.readthedocs.org/en/latest/?badge=latest)

# Disclaimer
While I'm still using this as a test ground to learn, the script itself has at least gotten somewhat useful. Feel free to let me know if you find things that aren't right. For now, it will do very basic things. For loops, while loops, List Comprehensions, arithmetic, booleans, etc. If you start wondering into a lot of built-in commands or methods, you probably will not have success.

For more information on what is and isn't implemented, check out WhatIsImplemented.md

For examples of what is possible, probably the best resource right now is the unit tests. I'll post more detailed examples later.

# Docs
Please see my ReadTheDocs for the most updated documentation: http://pysym.readthedocs.org/en/latest

# Install
## Pypi
pySym is now structured as a python package. You can use pip to install it:

```bash
$ git clone https://github.com/bannsec/pySym.git && cd pySym
$ (optional) virtualenv --python=$(which python3) pySym && . pySym/bin/activate
(pySym)$ pip install .
```

## Docker
pySym has a docker build for easy install and use. Just do the following:

```bash
$ sudo docker pull bannsec/pysym
$ sudo docker run -it --rm bannsec/pysym
```

# Tests
Just open up your environment and run ``pytest`` from the root directory.

```bash
$ workon pySym
(pySym)$ pytest
```

# Basic/Medium Example
Since the first example, I've implemented more things. It's still very much in development, but you can do better things with it now. Here's an example program:

```python
def test(x,y):
    out = 2
    while x < y:
        out *= x
        x += 1

    return out

x = 0
z = 0
while x < 5:
    y = 0
    while y < 3:
        z += test(x,y)
        y += 1
    x += 1
```

You can use a path group to automagically walk through the program as follows. First, save that example as 'test.py'. Now, do the following:

```python
import pySym
proj = pySym.Project("./test.py")
pg = proj.factory.path_group()
pg.explore()
```

That will tell pySym to attempt to find all the paths through the program to completion. Once it completes, you can ask what the value of z was at completion.

```python
In [4]: pg
Out[4]: <PathGroup with 45 deadended, 1 completed>

In [5]: pg.completed[0].state.any_int('z')
Out[5]: 26
```

# Basic Example
A lot of the layout for pySym is shamelessly stolen from the `angr` project. If you're familiar with their calls, this will make sense to you.

As an example of what is currently working, take the following script:

```python
x = 1.5
y = 1
if x == 1:
    y = 2
else:
    y += x
```

While basic, it can show how stepping through a program works. The following python script excersizes this functionality:

```python
from pySym.pyPath import Path
import ast
import logging
from pySym import Colorer
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

source = """
x = 1.5
y = 1
if x == 1:
    y = 2
else:
    y += x
"""
b = ast.parse(source).body
p = Path(b,source=source)
p = p.step()[0]
p = p.step()[0]
ifSide,elseSide = p.step()
elseSide = elseSide.step()[0]
```

Note that I put the source inline. It doens't have to be. You could read it from a file or really anywhere else that gives you a string. What happens in this script is the following:

b = ast.parse(source).body -- This call parses out the mini script into functional blocks that we use.

p = Path(b,source=source) -- This sets up our initial path variable. For now, this starts at the top of the script and works its way down.

p = p.step()[0] -- These are stepping through the program. The path itself does not get modified. However, a copy of the path returns. Note on the third step we encounter an if statement that causes the path to branch into two (taking both).

elseSide = elseSide.step()[0] -- Perform our final step, executing "y += x"

We can see if our given path is viable by checking path.state.isSat()

```python
In [2]: ifSide.state.isSat()
Out[2]: False

In [3]: elseSide.state.isSat()
Out[3]: True
```

As expected, the else is the only viable path through here. We can also ask what the variable should be at this point:

```python
In [4]: elseSide.state.any_real('y')
Out[4]: 2.5
```

Again, nothing fancy but it does give us the value we would expect from this path. If we wanted to discover what this elsePath looked like from start to finish, we can ask that as well:

```python
In [5]: elseSide.printBacktrace()
 Line 2  x = 1.5     <_ast.Assign object at 0x7f9263f8a438>    
 Line 3  y = 1       <_ast.Assign object at 0x7f9263f8d080>    
 Line 4  if x == 1:  <_ast.If object at 0x7f926985b550>        
 Line 7      y += x  <_ast.AugAssign object at 0x7f9263f8d400> 
```

Much work left to do as I have only implimented a limited set of operations. However, this is pretty neat!

# To-Do
Here's a list of things I have left to implement. This is really just a subset of things, but these are high on my list.

* Due to needing loose matching, some expressions will likely fail to work as expected
 * Need to determine when this will happen
* Fix explore find=. It's not working correctly
* Create pyObjectManager.Dict
* Create pyObjectManager.Set
* Add automatic BitVector scaling
 * http://stackoverflow.com/questions/22568867/z3-bitvector-overflow-checking-from-python
 * http://stackoverflow.com/questions/14579377/z3py-how-to-extend-and-trunc-variables
* ifelse inline (x = 1 if 1 > 2 else 2)
* function calls (mostly completed)
 * starargs
* imports
* "global" keyword
* symbolic arrays
* function annotations
* built-in calls
 * print
 * Some done... need to update this...
