#!/bin/bash

git clone https://git.torproject.org/tor.git tor

cd tor
./autogen.sh
./configure \
  --disable-asciidoc \
  --disable-manpage \
  --disable-html-manual \
  --disable-unittests \
  --enable-pic
make -j$(nproc)
