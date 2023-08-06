#!/bin/bash

./tor_setup.sh
./build.sh

cd build
sudo make install
