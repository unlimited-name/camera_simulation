if [ -e $HOME/anaconda3/bin/conda ]; then
    eval "$($HOME/anaconda3/bin/conda shell.bash hook)"
    export BOOST_ROOT=$HOME/anaconda3
    export CPATH="$HOME/anaconda3/include:$CPATH"
    export LIBRARY_PATH="$LIBRARY_PATH:$HOME/anaconda3/lib"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/anaconda3/lib"
fi
if [ -e $HOME/root/bin/thisroot.sh ]; then
    source $HOME/root/bin/thisroot.sh
fi
if [ -e $HOME/Geant4/bin/geant4.sh ]; then
    source $HOME/Geant4/bin/geant4.sh
    export PYTHONPATH="$HOME/Geant4/lib:$PYTHONPATH"
fi
if [ -e /usr/local/cuda ]; then
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib/cuda/lib64"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib/cuda-11.0/lib64"
    export PATH=/usr/local/cuda-11.0/bin${PATH:+:${PATH}}
    export PATH=$PATH:/usr/local/cuda/bin
    export CUDA_HOME=$CUDA_HOME:/usr/local/cuda
fi