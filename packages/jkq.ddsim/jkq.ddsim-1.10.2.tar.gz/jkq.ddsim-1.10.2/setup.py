from setuptools import setup
import os

VERSION = "1.10.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="jkq.ddsim",
    description="jkq.ddsim is now mqt.ddsim",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["mqt.ddsim"],
    classifiers=["Development Status :: 7 - Inactive"],
)
