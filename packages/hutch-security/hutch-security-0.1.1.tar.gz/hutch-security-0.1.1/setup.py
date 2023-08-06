#!/usr/bin/env python3
"""Minimal setup for hutch-security."""
import os

from setuptools import find_namespace_packages, setup

# setupmeta does not seem to pull in metadata from namespace packages. As a result, we
# need to pull things in ourselves.
__version__ = "0.0.0"
__author__ = "Not Defined"

path = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(path, "hutch/security/__about__.py")).read())  # noqa: S102

# Let setupmeta handle all of the usual metadata from the project metadata.
setup(
    setup_requires="setupmeta",
    version=__version__,
    author=__author__,
    packages=find_namespace_packages(include="hutch.security.*"),
)
