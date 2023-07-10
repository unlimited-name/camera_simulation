echo "==========Hello World !============"
export WORK_DIR=${HOME}

echo "installing ROOT......"

cd ${WORK_DIR}
export VERSION_ROOT=6.22.02
sudo apt-get update
sudo apt-get -y install gfortran libpcre3-dev \
xlibmesa-glu-dev libglew-dev libftgl-dev \
libmysqlclient-dev libfftw3-dev libcfitsio-dev \
graphviz-dev libavahi-compat-libdnssd-dev \
libldap2-dev python-dev libxml2-dev libkrb5-dev \
libgsl0-dev qtwebengine5-dev \
dpkg-dev g++ binutils libx11-dev libxpm-dev libxft-dev \
 libxext-dev libgsl-dev libxerces-c-dev libxmu-dev libxi-dev freeglut3-dev libboost-all-dev
curl -O https://root.cern/download/root_v${VERSION_ROOT}.source.tar.gz
tar xf root_v${VERSION_ROOT}.source.tar.gz
mkdir ${WORK_DIR}/root-${VERSION_ROOT}/build-root && cd ${WORK_DIR}/root-${VERSION_ROOT}/build-root
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${HOME}/root -Dpython3=ON -Ddavix=OFF -Dminuit2=ON -Droofit=ON ${WORK_DIR}/root-${VERSION_ROOT}
cmake --build . --target install -j8

if [ -e $HOME/root/bin/thisroot.sh ]; then
    source $HOME/root/bin/thisroot.sh
    echo "ROOT installed!"
else
    echo "Failed to source ROOT ENV. Please review the installation."
fi

echo "==============================="
