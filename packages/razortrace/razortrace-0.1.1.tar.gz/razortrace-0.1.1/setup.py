# -*- coding: UTF-8 -*-
"""
Setup
"""
import sys
import os
from setuptools import setup

NAME = "razortrace"


def get_version(*args):
    version_file = "razortrace/__version__.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()


URL = "https://github.com/manbehindthemadness/razortrace"
DESCRIPTION = "Straight forward memory leak detection"
LONG_DESCRIPTION = \
    """
    Razortrace is a memory diagnostic tool based on the ``tracemalloc`` library. It's aim is to provide rapid identification 
    of memory leaks and produce straightforward, human-readable reports.
    """


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported')

setup(
    name="razortrace",
    version=get_version("razortrace"),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords="malloc, memory, leak, trace",
    author="manbehindthemadness",
    author_email="manbehindthemadness@gmail.com",
    url=URL,
    license="MIT",
    packages=get_packages('razortrace'),
    include_package_data=True,
    package_data={'razortrace': []}
)
