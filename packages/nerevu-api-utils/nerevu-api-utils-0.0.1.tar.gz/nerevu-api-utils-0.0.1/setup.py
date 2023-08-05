#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pkutils

from os import path as p
from setuptools import setup

PARENT_DIR = p.abspath(p.dirname(__file__))

sys.dont_write_bytecode = True
requirements = list(pkutils.parse_requirements("requirements.txt"))
dev_requirements = list(pkutils.parse_requirements("dev-requirements.txt"))
dependencies = sorted(pkutils.parse_requirements("requirements.txt", dep=True))
module = pkutils.parse_module(p.join(PARENT_DIR, "api_utils.py"))
license = module.__license__
version = module.__version__
project = module.__title__
description = module.__description__
user = "reubano"

# Setup requirements
setup_require = [r for r in dev_requirements if "pkutils" in r]

setup(
    name=project,
    version=version,
    description=description,
    author=module.__author__,
    author_email=module.__email__,
    url=pkutils.get_url(project, user),
    download_url=pkutils.get_dl_url(project, user, version),
    py_modules=["api_utils"],
    include_package_data=True,
    package_data={"helpers": ["helpers/*"]},
    install_requires=requirements,
    extras_require={"develop": dev_requirements},
    setup_requires=setup_require,
    dependency_links=dependencies,
    tests_require=dev_requirements,
    license=license,
    zip_safe=False,
    keywords=[project] + description.split(" "),
    classifiers=[
        pkutils.get_license(license),
        pkutils.get_status(version),
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    platforms=["MacOS X", "Windows", "Linux"],
)
