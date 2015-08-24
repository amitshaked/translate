#!/bin/sh
mkdir externals
cd externals
wget -O - http://kheafield.com/code/kenlm.tar.gz |tar xz
cd kenlm
bjam -j12 linkflags=-lboost_thread-mt
python setup.py build
cd ../..
ln -s externals/kenlm/build/lib.*/kenlm.so kenlm.so
