========================
Examples
========================

Tokyo Westerns CTF 2017: My Simple Cipher
=========================================
External Writeup: `BannSecurity.com <https://bannsecurity.com/index.php/home/10-ctf-writeups/44-tokyo-westerns-ctf-2017-my-simple-cipher>`_

Prime Finder
========================

Let's recreate a simple problem of finding all the primes under 50. Stealing
and modifying some code from the internet, we can use the following python code
to do just that.

.. code-block:: python

    # Enable logging if you want. It's faster without.
    #import logging
    #logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    from pySym.pyPath import Path
    from pySym import ast_parse
    from pySym import Colorer
    from pySym.pyPathGroup import PathGroup

    source = """
    def isprime(n):

        # 0 and 1 are not primes
        if n < 2:
            return 0

        # 2 is the only even prime number
        if n == 2:
            return 1

        # all other even numbers are not primes
        if n % 2 == 0:
            return 0

        # range starts with 3 and only needs to go up
        # the square root of n for all odd numbers
        for x in range(3, int(n**0.5) + 1, 2):
            if n % x == 0:
                return 0

        return 1

    x = [x for x in range(50) if isprime(x) == 1]
    """

    b = ast_parse.parse(source).body
    p = Path(b,source=source)
    pg = PathGroup(p,discardFailures=True)

The first two lines are just to add more logging. If you're not interested in
watching scrolling text, just leave those two out. Aside from that, the rest is
self explanatory. As of writing, I have not implemented Bools yet, so this is
why I'm returning integer 1 or 0. The end effect is the same, however.

As written, this code will symbolically execute without special changes. To do
so, just execute:

.. code-block:: python

    pg.explore()

This will cause `pySym` to start exploring this state and finding valid paths.
Since we're only dealing with concrete variables, there will be one valid path
through. However, there will be many deadended paths since `pySym` will take
every branch along the way.

Also note, I used "discardFailures=True" in PathGroup. This is because with
this option enabled, you won't be wasting memory of your computer with
deadended paths. When there are many such paths, or if the paths are
complicated, the total memory used by paths you're not interested in can become
high. This option allows you to immediately forget those paths and thus reduce
your memory profile.

Once done, we can confirm that the expected results were attained:

.. code-block:: python

    In [7]: pg
    Out[7]: <PathGroup with 1 completed>

    In [8]: x = pg.completed[0].state.getVar('x')

    In [9]: print(x)
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

The first command simply shows us that our path group has 1 completed path. As
mentioned above, there would be many more deadended paths if we hadn't set
discardFailures to True. The second command reaches into our only completed
path (index 0) and asks the state to give us the pyObjectManager object for
variable named 'x'. We can do many things with this variable at this point,
however for the purposes of this example, we simply print out the variable. It
will pause for a few moments as z3 solves constraints for us and `pySym` puts
it into the proper representation (a list).


