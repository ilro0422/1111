========================
pySym Quick-Start
========================

Running Your First Program
==========================

Assuming that you have already `installed <installation.html>`_ pySym, actiate
your virtual environment and load up a source::

   $ workon pySym
   (pySym)$ ipython

+++++++++++++++++
Automated Loading
+++++++++++++++++

Assuming you have a program you want to symbolically execute called
`my_test_program.py`, you can do so with the following lines:

.. code-block:: python

   In [1]: import pySym

   In [2]: proj = pySym.Project("my_test_program.py")

   In [3]: pg = proj.factory.path_group()

You can now run it by simply executing:

.. code-block:: python
    
    In [4]: pg.explore()

+++++++++++++++++++++
Manually From Strings
+++++++++++++++++++++

You can also load your script directly via python string. The following example
loads it from a file:

.. code-block:: python

   In [1]: from pySym.pyPath import Path

   In [2]: import ast

   In [3]: from pySym import Colorer

   In [4]: from pySym.pyPathGroup import PathGroup

   In [5]: with open("test","r") as f:
      ...:         b = ast.parse(source).body
      ...:         p = Path(b,source=source)
      ...:         pg = PathGroup(p)

You can now run it by simply executing:

.. code-block:: python
    
    In [6]: pg.explore()

See the `examples <examples.html>`_ page for example programs.
