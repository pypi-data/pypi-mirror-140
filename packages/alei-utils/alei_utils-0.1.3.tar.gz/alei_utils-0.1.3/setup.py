from alei_utils import __version__

from collections import OrderedDict

import os
import setuptools

ENV_VERSION = os.getenv('VERSION')

version = __version__ if ENV_VERSION is None else ENV_VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="alei_utils",
    version=f"{version}",
    author="GPAM",
    author_email="gpam@gmail.com",
    description="Alei utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://gitlab.com/gpam/alei/service/alei-utils",
    packages=setuptools.find_packages(include=["alei_utils", "alei_utils.*"]),
    python_requires=">=3.6.0",
    project_urls=OrderedDict(
        (
            ("Documentation", "https://gitlab.com/gpam/alei/service/alei-utils"),
            ("Code", "https://gitlab.com/gpam/alei/service/alei-utils"),
            ("Issue tracker", "https://gitlab.com/gpam/alei/service/alei-utils/-/issues"),
        )
    ),
    install_requires=[],
    tests_require=[
        "pytest",
        "flake8",
        "pytest-cov",
        "pytest-mock",
        "isort",
        "black",
    ],
    setup_requires=["setuptools>=38.6.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
)
