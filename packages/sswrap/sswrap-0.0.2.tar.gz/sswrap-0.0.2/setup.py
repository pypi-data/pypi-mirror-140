#!/usr/bin/env python
import os

from setuptools import setup, find_packages

try:
    with open("README.md") as f:
        readme = f.read()
except IOError:
    readme = ""


def _requires_from_file(filename):
    return open(filename).read().splitlines()


here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace('"', '').replace("'", '')
                for line in open(os.path.join(here, 'sswrap', '__init__.py'))
                if line.startswith('__version__ = ')),
                '0.0.dev0')

setup(
    name="sswrap",
    version=version,
    url="https://github.com/dmiyakawa/sswrap",
    author="Daisuke Miyakawa",
    author_email='2149473+dmiyakawa@users.noreply.github.com',
    maintainer='Daisuke Miyakawa',
    maintainer_email='2149473+dmiyakawa@users.noreply.github.com',
    description='Spreadsheet and Worksheet wrapper',
    long_description=readme,
    packages=find_packages(),
    install_requires=_requires_from_file("requirements.txt"),
    license="Apache 2",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      sswrap = pypipkg.scripts.command:main
    """,
)
