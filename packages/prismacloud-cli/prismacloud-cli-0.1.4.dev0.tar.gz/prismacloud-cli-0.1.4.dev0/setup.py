import os
from setuptools import setup
import logging
from importlib import util
from os import path

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

spec = util.spec_from_file_location(
    "prismacloud_cli.version", os.path.join("prismacloud_cli", "version.py")
)

# noinspection PyUnresolvedReferences
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore
version = mod.version  # type: ignore

setup(
    extras_require={},
    install_requires=[
        "requests",
        "pandas",
        "jsondiff",
        "importlib",
        "ipython",
        "argh",
        "argparse",
        "tabulate"
    ],
    name = "prismacloud-cli",
    version = version,
    author = "Steven de Boer",
    author_email = "stdeboer@paloaltonetworks.com",
    maintainer = "Simon Melotte",
    maintainer_email = "smelotte@paloaltonetworks.com",
    description = ("Prisma Cloud CLI"),
    license = "BSD",
    keywords = "prisma cloud cli",
    url = "https://github.com/se-cloud-emea/prismacloud-cli",
    packages=['prismacloud_cli'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License"
    ],
    scripts=["bin/pc"],

)