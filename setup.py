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
    keywords=["Android", "adb"],
    description="A friendly android adb command-line tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/litefeel/adbtool",
    author="litefeel",
    author_email="litefeel@gmail.com",
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    platforms="any",
    install_requires=["litefeel-pycommon", "PyYAML", "semantic_version"],
    scripts=[],
    entry_points={"console_scripts": ["adbt = adbtool.adbtool:main"]},
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.9",
)
