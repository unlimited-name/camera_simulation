echo "installing chroma......"

cd ${HOME}
sudo apt-get install -y libboost-all-dev
pip install pygame
wget -O chroma_version.json https://api.github.com/repos/BenLand100/chroma/git/refs/heads/master
git clone https://github.com/BenLand100/chroma

cd chroma
cp ${HOME}/installation/chroma.patch ${PWD}
patch -p1 < chroma.patch
python setup.py develop

echo "chroma installed!"