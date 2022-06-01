========================
Installing pySym
========================

pip install
========================
``pySym`` has been refactored to be a proper python package. This is now the
easiest means of installing this library. To do so, simply clone this repo and
run pip install::

    $ git clone https://github.com/bannsec/pySym.git
    $ cd pySym
    $ pip install .

Note that it's recommended to install into a python virtual environment instead
of your system environment.

Docker install
========================
You can also install ``pySym`` using a pre-build Docker container. This is
setup as an auto-build image, so you will always be up-to-date::

    $ sudo docker pull bannsec/pysym
    $ sudo docker run -it --rm bannsec/pysym


setup.sh (depreciated)
========================

If you run on Ubuntu (or derivative) this will probably work for you. It
completely automates the setup process that is outlined below. Usage is as
follows::

   bash$ ./setup.sh

That's it. You're all setup. Note that if you want to remove ``pySym`` that was
installed this way, you can use the ``uninstall.sh`` script to do so.

Manual Install
========================

If the auto install doesn't work for some reason, the following manual steps
can be taken to install.

Install Dependencies
------------------------

Dependencides for ``pySym`` include:

* ``virtualenv`` (Python's virtual environment)
* ``gcc``
* ``make``
* ``python3``
* ``git``

For Ubuntu, the following line works for me::

   $ sudo apt-get update
   $ sudo apt-get install -y make gcc g++ virtualenv virtualenvwrapper python3 git

``virtualenvwrapper`` is recommended to make switching between environments
easier, but it's not required.

Set up your Virtual Environment
--------------------------------

It's not necessary to create a virtual environment, but it's good practice and
keeps things clean. Perform the following steps to set up a virtual environment
named pySym::

   $ mkdir -p ${HOME}/.virtualenvs/pySym
   $ virtualenv -p $(which python3) ${HOME}/.virtualenvs/pySym

Now you should activate it so that you can work inside it. If you have
virtualenvwrappers installed, you can do the following::

   $ workon pySym

If you don't have that installed, or for whatever reason it isn't working, you
can source the virtualenv directly to activate your environment::

   $ source "${HOME}/.virtualenvs/pySym/bin/activate"

You should see "(pySym)" next to your command prompt to indicate the
environment is activated properly.

Install Python Packages
------------------------

With your virtual environment activated, install the Python dependencies. From
the root of the repository, do the following::

   (pySym)$ pip install -r requirements.txt

The following are optional packages for running the py.test unit tests. If
you're not planning on running the tests you can omit these::

   (pySym)$ pip3 install pytest
   (pySym)$ pip3 install python-coveralls
   (pySym)$ pip3 install coverage
   (pySym)$ pip3 install pytest-cov
   (pySym)$ pip3 install pytest-xdist

Install Microsoft Z3 with Python Bindings
------------------------------------------

Time to install Microsoft's Z3. This step will take a while to compile
everything, so be patient. First thing, create the working directory and git
clone the z3 tool::

   (pySym)$ mkdir -p ${HOME}/opt/pySymZ3
   (pySym)$ cd ${HOME}/opt
   (pySym)$ git clone https://github.com/Z3Prover/z3.git pySymZ3
   (pySym)$ cd pySymZ3

Perform the build and install. As noted, this could take a while::

   (pySym)$ python scripts/mk_make.py --python
   (pySym)$ cd build
   (pySym)$ make
   (pySym)$ make install

Performing these steps while having your Python virtual environment activated
will cause the install to be performed into that environment. This also means
that you do not need root priviledges for any of this install.

You are now ready to use ``pySym``.
