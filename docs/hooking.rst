================
Symbolic Hooking
================

What is Hooking
===============

Hooking is a means to interject your own commands into the symbolic execution
of the application. For instance, a common reason to hook a function or part of
a function is to provide your own symbolic summary for it. In this way, you can
jump out of the symbolically executed script, back into the engine and tell
`pySym` how to keep that section symbolic.

One quick example is, if you consider an if statement nested inside a while
loop, as follows:

.. code-block:: python

   def my_function(my_list):
     output = []
     for element in my_list:
        if element == 0:
           output.append("zero")
        else:
           output.append("one")
     return output

In the above example, that ``if`` statement inside the ``for`` loop would actually
cause pySym to state split for each element. Depending on the size of the input
list and how symbolic the input actually is, this could cause a path explosion
issue. One way around that is to hook ``my_function`` and create a summary for
it.

How to Hook
===========
At present, hooking in `pySym` is accomplished via the `pySym.Project.hook`
method.

See the method documentation for more details:

:meth:`pySym.Project.Project.hook`
