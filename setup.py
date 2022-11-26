#!/usr/bin/env python

import re
from setuptools import find_packages, setup

VERSION_FILE = "fdk_extension/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                      version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Unable to find version string in {VERSION_FILE}.")

with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name="fdk_extension",
    version=version,
    description="FDK Extension helper library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Meet Koriya",
    author_email="meetkoriya@fynd.com",
    url="https://github.com/gofynd/fdk-extension-python",
    project_urls={
        "Source Code": "https://github.com/gofynd/fdk-extension-python",
    },
    download_url="https://pypi.org/project/tweepy/",
    packages=find_packages(
        exclude=("examples*", )
    ),
    install_requires=[
        "fdk_client@git+https://github.com/gofynd/fdk-client-python.git@0.1.27#egg=fdk_client",
        "sanic>=22.9.0",
        "aioredis>=2.0.0",
        "structlog>=20.1.0"
    ],
    keywords=["FDK extension python", "Extension", "FDK"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only"
    ],
)