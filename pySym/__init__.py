#!/usr/bin/env python3

from .Project import Project

"""
import ast
import argparse
import logging
import symbolicExecutor
from pySym import Colorer

logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('main')


parser = argparse.ArgumentParser(description='Symbolically Execute A Python Script.')
parser.add_argument('script', type=str, nargs=1,
                   help='Script file name')
args = parser.parse_args()

#print(args)
script = args.script[0]

# Load it
logger.debug("Loading script {0}".format(script))
with open(script,"r") as f:
    body = ast.parse(f.read()).body

# Run it
symbolicExecutor.runBody(body)
"""
