export VERSION_GEANT4=10.05.p01
export VERSION_ROOT=6.22.02

cd $HOME
if [ -e $HOME/geant4.${VERSION_GEANT4}.tar.gz ]; then
    rm geant4.${VERSION_GEANT4}.tar.gz
fi
if [ -e $HOME/root_v${VERSION_ROOT}.source.tar.gz ]; then
    rm root_v${VERSION_ROOT}.source.tar.gz
fi
if [ -e $HOME/geant4.${VERSION_GEANT4} ]; then
    rm -rf $HOME/geant4.${VERSION_GEANT4}
fi
if [ -e $HOME/root-${VERSION_ROOT} ]; then
    rm -rf $HOME/root-${VERSION_ROOT}
fi
if [ -e $HOME/cuda_11.0.3_450.51.06_linux.run ]; then
    rm cuda_11.0.3_450.51.06_linux.run
fi