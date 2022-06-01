========================
About pySym
========================

Introduction to ``pySym``
==========================

``pySym`` is a python application that utilizes the Microsoft Z3 Theorem
Prover to solve it's constraints. The goal for this application is to
faithfully execute *basic* python scripts and provide a means to analyze them
symbolically. Note that this application will not allow you to test your python
apps for python interpreter version dependent bugs. It will attempt to follow
what Python *should* be doing and thus would be more appropriate for the
following two cases:

1) Finding logic bugs in your application.
2) Discovering possibly unused code segments
3) Generating test cases
4) Rapidly prototyping concepts for symbolic analysis

Python Versions
========================
pySym is written in Python 3 and will parse Python 3 code. It will likely not
parse Python 2 code, however small code can simple be auto-upgraded if need be
by the 2to3 script.

pySym Weaknesses
========================
``pySym`` is not, nor will it ever be, a complete Python Symbolic Execution
Engine. Scripted languages are rapidly evolving, and Python is no exception.
Rapid evolution aside, even between minor versions of Python there are many
small changes that will cause unintended code paths. Likely it is not feasible
for any script based Symbolic Execution of Python to be that thorough.

If your goal is faithful Python symbolic exeuction to any given Python
major/minor versions, I'd recommend looking at a project called `CHEF 
<http://dslab.epfl.ch/proj/chef/>`_. This project is a novel approach whereby
the authors instrument the source interpreter with the `S2E
<https://s2e.epfl.ch/>`_ framework thereby causing very thorough code path
generation.

pySym Strengths
========================
``pySym`` is an attempt at generalizing Python Symbolic Execution utilizing
Python itself. One major downfall that approaches such as CHEF have is that it
is unable to make symbolic input aside from int and string types. With
``pySym``, already it has the ability to produce fully symbolic ints, floats,
lists, and strings. When more datatypes are added, they will have the ability
to be fully symbolic as well. This is important when you want to stress test
symbolic Dictionaries or other more complex objects.

It is also easy to use. Simply run the installer, load up the script you want
to execute (with or without changes), and tell ``pySym`` to explore. It's not
dependent on compiling special versions of applications or using strange
commands that you're not quite sure what you're doing. You can be up and
running in as little as 10 minutes.

As a follow-on, because everything can be symbolic and you can prototype Python
code in general quickly, ``pySym`` gives you a way to explore concepts without
needing to be a symbolic exeuction expert. Simply write your code as you would
normally for Python, then run it through ``pySym``.
