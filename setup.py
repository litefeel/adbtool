import os

from setuptools import find_packages, setup

_DIR_OF_THIS_SCRIPT = os.path.split(__file__)[0]
_VERSION_FILE_NAME = "version.txt"
_VERSION_FILE_PATH = os.path.join(_DIR_OF_THIS_SCRIPT, "adbtool", _VERSION_FILE_NAME)
_README_FILE_NAME = "README.md"
_README_FILE_PATH = os.path.join(_DIR_OF_THIS_SCRIPT, _README_FILE_NAME)


with open(_VERSION_FILE_PATH, "r") as fh:
    version = fh.read().strip()

with open(_README_FILE_PATH, "r") as fh:
    long_description = fh.read()

setup(
    name="adbtool",
    version=version,
    keywords=("Android", "adb"),
    description="eds sdk",
    long_description="eds sdk for python",
    license="MIT Licence",
    url="https://www.litefeel.com",
    author="litefeel",
    author_email="litefeel@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["litefeel-pycommon"],
    scripts=[],
    entry_points={"console_scripts": ["adbtool = adbtool.adbtool:main"]},
)