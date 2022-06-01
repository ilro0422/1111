#!/bin/sh
py.test --forked -d -n auto --cov=. --cov-config=.coveragerc tests/
