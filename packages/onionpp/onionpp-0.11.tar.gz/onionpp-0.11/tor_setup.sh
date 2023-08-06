#!/bin/bash

if [ ! -d tor ]; then
  git clone https://git.torproject.org/tor.git tor
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
