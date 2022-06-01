"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import os

here = path.abspath(path.dirname(__file__))

#with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()
long_description = "See website for more info."

dev_tools = ['pytest','python-coveralls','coverage','pytest-cov','pytest-xdist','ipython', 'gprof2dot', 'sphinx', 'sphinx_rtd_theme']

#
# Install z3 or no?
# 

install_requires=['prettytable','enforce']

# Defaulting RTD builds to use pip z3 solver
if "PYSYM_NO_Z3" not in os.environ or os.environ.get('READTHEDOCS', None) == 'True':
    install_requires.append('z3-solver')

setup(
    name='pySym',
    version='0.0.2',
    description='Symbolic execution of python source.',
    long_description=long_description,
    # The project's main homepage.
    url='https://github.com/bannsec/pySym',
    author='Michael Bann',
    author_email='self@bannsecurity.com',
    license='MIT',
    classifiers=[
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    keywords='symbolic execution python',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'longer_tests']),
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=dev_tools,
    extras_require={
        'dev': dev_tools,
    },

    #entry_points={
    #    'console_scripts': [
    #        'pySym = pySym.pySym:main',
    #    ],
    #},

)

