#!/bin/bash
echo "==========Hello World !============"
echo "==============================="

cd ${HOME}

echo "detecting CUDA......"
if [ -e /usr/local/cuda ]
then
    echo "CUDA already installed. "
else
    echo "installing CUDA......"
    echo "Warning: the installed CUDA version may not be compatible with the GPU."
    wget http://developer.download.nvidia.com/compute/cuda/11.0.3/local_installers/cuda_11.0.3_450.51.06_linux.run
    sudo sh cuda_11.0.3_450.51.06_linux.run

    #sudo systemctl enable nvidia-persistenced
    #sudo cp /lib/udev/rules.d/40-redhat.rules /etc/udev/rules.d 
    #sudo sed -i 's/SUBSYSTEM!="memory",.*GOTO="memory_hotplug_end"/SUBSYSTEM=="*", GOTO="memory_hotplug_end"/' /etc/udev/rules.d/40-redhat.rules
    echo "CUDA installed!"
    echo "==============================="
fi

echo "installing CUDA Toolkit via pip......"
if [ -e $HOME/anaconda3 ]
then
    conda install pip
    pip install --upgrade setuptools pip wheel
    pip install nvidia-pyindex

    pip install nvidia-cuda-runtime-cu12
else
    echo "Anaconda not detected. Please run anaconda.sh first."
fi

echo "installing PyCUDA via pip......"
if [ -e $HOME/anaconda3 ]
then
    pip install pycuda
else
    echo "Anaconda not detected. Please run anaconda.sh first."
fi

#wget https://files.pythonhosted.org/packages/5e/3f/5658c38579b41866ba21ee1b5020b8225cec86fe717e4b1c5c972de0a33c/pycuda-2019.1.2.tar.gz
#tar xzf pycuda-2019.1.2.tar.gz && cd pycuda-2019.1.2 # if you're not there already
#python configure.py --cuda-root=/usr/local/cuda --cudadrv-lib-dir=/usr/lib

#make -j8
#sudo env PATH=$PATH
#sudo python setup.py install

# lines to check installation

#dpkg -l | grep -i gcc
#dpkg -l | grep -i linux-headers
#sudo apt-get install gcc linux-kernel-headers
#sudo sh NVIDIA-Linux-x86_64-xxxx.run --ui=none --disable-nouveau --no-install-libglvnd --dkms -s