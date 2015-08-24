#!/bin/sh
mkdir -p externals
cd externals
wget -O - https://moses-suite.googlecode.com/files/giza-pp-v1.0.7.tar.gz |tar xz
sed -i 's/-DBINARY_SEARCH_FOR_TTABLE//' giza-pp/GIZA++-v2/Makefile
cd ..
make -C externals/giza-pp
