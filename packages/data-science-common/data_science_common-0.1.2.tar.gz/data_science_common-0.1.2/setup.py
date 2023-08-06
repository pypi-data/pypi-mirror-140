from setuptools import setup
import os

def get_long_description():
    with open(
        os.path.join(os.path.dirname(__file__), "README.md"),
        encoding="utf8"
    ) as fp:
        return fp.read()


setup(
    name="data_science_common",
    version=os.getenv('VERSION'),
    description="UNDER CONSTRUCTION: A simple python library for facilitating analysis",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Ryan Kelley",
    url="https://github.com/kelleyrw/data_science_common",
    license="Apache License, Version 2.0",
    py_modules=["pids"],
)
