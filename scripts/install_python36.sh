#!/usr/bin/env bash
set -eou pipefail


# install python 3.6 on ubuntu 14.4
# travis-ci has not installed python 3.6 yet

cd ../
PYVER="3.6.0"
wget https://www.python.org/ftp/python/$PYVER/Python-$PYVER.tgz
tar -xvf Python-$PYVER.tgz
cd Python-$PYVER
./configure --prefix=/usr/local/python-$PYVER>log1.log && make>log2.log && sudo make install>log3.log
python --version
echo "ls -lha /usr/bin"
ls -lha /usr/bin
echo "ls -lha /usr/local"
ls -lha /usr/local
sudo rm -f /usr/bin/python
ls -lha /usr/local/python-$PYVER/bin
pyshortver=`echo $PYVER|awk -F. '{printf "%d.%d\n", $1,$2}'`
echo "sudo ln -fs /usr/local/python-$PYVER/bin/python$pyshortver /usr/bin/python"
sudo ln -fs /usr/local/python-$PYVER/bin/python$pyshortver /usr/bin/python
sudo chmod +x /usr/bin/python
cd $TRAVIS_BUILD_DIR

echo "ssss"
echo "python -V"
python -V