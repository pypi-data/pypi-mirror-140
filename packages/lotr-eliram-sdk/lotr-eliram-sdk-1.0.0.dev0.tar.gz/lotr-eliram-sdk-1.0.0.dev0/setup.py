#!/usr/bin/env python
# This is a setup.py shim and NOTHING else should be added to it!!!
# we only need the setup.py file for local editable development. `pip install -e .`
import setuptools

if __name__ == "__main__":
    setuptools.setup()
# DO NOT ADD NOTHING TO THIS FILE. Everything should be in the pyproject.toml and setup.cfg
