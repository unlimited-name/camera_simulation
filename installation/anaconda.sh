echo "==========Hello World !============"
sudo apt-get update
sudo apt-get install -y curl wget cmake
#dos2unix chroma_env.sh
sudo cp chroma_env.sh /etc/profile.d/

echo "==============================="

echo "installing anaconda......"

# using the anaconda version default with python3.7
# if prefering python3.6, consider anaconda-2018
curl -O https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
chmod +x Anaconda3-2019.10-Linux-x86_64.sh
./Anaconda3-2019.10-Linux-x86_64.sh -b -p ${HOME}/anaconda3
rm Anaconda3-2019.10-Linux-x86_64.sh
eval "$($HOME/anaconda3/bin/conda shell.bash hook)"
conda init

conda install -y -c anaconda boost cmake
#conda install -y -c conda-forge pymesh2

source /etc/profile

echo "anaconda installed!"
echo "restart the shell to continue installation"
echo "==============================="