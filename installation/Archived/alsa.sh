#!/bin/bash
echo "==========Hello World !============"
export WORK_DIR=${HOME}
echo "==============================="

cd /usr/src
git clone git://git.alsa-project.org/alsa.git alsa
git clone git://git.alsa-project.org/alsa-python.git alsa-python
mkdir alsa
cd alsa
cp /downloads/alsa-* .

bunzip2 alsa-driver-xxx
tar -xf alsa-driver-xxx
cd alsa-driver-xxx
./configure --with-cards=dummy --with-sequencer=yes ; make ; make install

apt-cache depends python-pygame

sudo cp asound.conf /etc/asound.conf