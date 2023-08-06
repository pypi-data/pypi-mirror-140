#!/bin/bash

git submodule update --init

if [ ! -d tor ]; then
  echo "Tor directory not found!"
  exit
fi

cd tor
./autogen.sh
./configure \
  --disable-asciidoc \
  --disable-manpage \
  --disable-html-manual \
  --disable-unittests \
  --enable-pic
make -j$(nproc)
