from setuptools import setup, find_packages

setup(
    name="adbtool",
    version="1.0",
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
