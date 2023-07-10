FROM ubuntu:20.04 as build-anaconda
MAINTAINER Benjamin Land <benland100@gmail.com>

USER root
WORKDIR /opt/
RUN apt-get update && apt-get install -y curl git \
    && curl -O https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh \
    && chmod +x Anaconda3-2021.05-Linux-x86_64.sh \
    && ./Anaconda3-2021.05-Linux-x86_64.sh -b -p /opt/anaconda3 \
    && rm Anaconda3-2021.05-Linux-x86_64.sh \
    && apt-get purge -y --auto-remove curl git
COPY chroma_env.sh /etc/profile.d/
SHELL ["/bin/bash", "-l", "-c"] 
RUN conda install -y -c anaconda boost cmake


FROM ubuntu:20.04 AS build-root
MAINTAINER Benjamin Land <benland100@gmail.com>

USER root
COPY chroma_env.sh /etc/profile.d/
COPY --from=build-anaconda /opt/anaconda3 /opt/anaconda3
ARG DEBIAN_FRONTEND=noninteractive
ARG VERSION_ROOT=6.22.02

WORKDIR /opt/
SHELL ["/bin/bash", "-l", "-c"] 
RUN apt-get update \
    && set -x; buildDeps='dpkg-dev gcc g++ binutils libx11-dev libxpm-dev libxft-dev libxext-dev libgsl-dev libfftw3-dev libpcre3-dev' \
    && apt-get install -y $buildDeps \
    && curl -O https://root.cern/download/root_v${VERSION_ROOT}.source.tar.gz \
    && tar xf root_v${VERSION_ROOT}.source.tar.gz \
    && rm root_v${VERSION_ROOT}.source.tar.gz \
    && mkdir

WORKDIR /opt/root-${VERSION_ROOT}/build-root
RUN cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/root -Dpython3=ON -Ddavix=OFF -Dminuit2=ON -Droofit=ON /opt/root-${VERSION_ROOT}
RUN make -j12
RUN make install
RUN rm -rf /opt/root-${VERSION_ROOT}

FROM ubuntu:20.04 as build-geant4
MAINTAINER Benjamin Land <benland100@gmail.com>

USER root
RUN apt-get update && apt-get install -y curl git
COPY chroma_env.sh /etc/profile.d/
SHELL ["/bin/bash", "-l", "-c"] 
COPY --from=build-anaconda /opt/anaconda3 /opt/anaconda3
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y dpkg-dev gcc g++ binutils libx11-dev libxpm-dev libxft-dev libxext-dev libgsl-dev libfftw3-dev libpcre3-dev
COPY --from=build-root /opt/root /opt/root
RUN apt-get update && apt-get install -y libxerces-c-dev libxmu-dev libxi-dev freeglut3-dev

WORKDIR /opt/
RUN curl -O https://geant4-data.web.cern.ch/geant4-data/releases/geant4.10.05.p01.tar.gz
RUN tar xf geant4.10.05.p01.tar.gz
RUN rm geant4.10.05.p01.tar.gz
WORKDIR /opt/geant4.10.05.p01/build-g4
RUN cmake -DCMAKE_BUILD_TYPE=Release -DGEANT4_INSTALL_DATA=ON -DCMAKE_INSTALL_PREFIX=/opt/geant4 -DGEANT4_USE_GDML=ON -DGEANT4_USE_OPENGL_X11=ON -DGEANT4_USE_XM=OFF /opt/geant4.10.05.p01
RUN make -j12
RUN make install
WORKDIR /opt/geant4.10.05.p01
COPY g4py.4.10.05.p01.patch ./
RUN git apply g4py.4.10.05.p01.patch
WORKDIR /opt/geant4.10.05.p01/build-g4py
RUN BOOST_ROOT=/opt/anaconda3 cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/geant4 /opt/geant4.10.05.p01/environments/g4py
RUN make -j12 
RUN sed -i 's/install: preinstall/install:/' Makefile
RUN find . -name '*.cmake' -exec sed -i -n -E '/\.pyc|\.pyo/!p' {} \;
RUN sed -i -E 's/(.*G4LossTableManager.Instance.*)/#\1/' source/python3/__init__.py
RUN make install
RUN rm -rf /opt/geant4.10.05.p01


FROM ubuntu:20.04
MAINTAINER Benjamin Land <benland100@gmail.com>

USER root
RUN apt-get update && apt-get install -y curl git
SHELL ["/bin/bash", "-l", "-c"] 
COPY --from=build-anaconda /opt/anaconda3 /opt/anaconda3
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y dpkg-dev gcc g++ binutils libx11-dev libxpm-dev libxft-dev libxext-dev libgsl-dev libfftw3-dev libpcre3-dev
COPY --from=build-root /opt/root /opt/root
RUN apt-get update && apt-get install -y libxerces-c-dev libxmu-dev libxi-dev freeglut3-dev
COPY --from=build-geant4 /opt/geant4 /opt/geant4
RUN apt-get update && apt-get install -y libgmp-dev libmpfr-dev libgmpxx4ldbl zip unzip patchelf
# need this env for PyMesh, but must remove it because it breaks dbus
COPY chroma_env.sh /etc/profile.d/ 
RUN git clone --branch v0.3 https://github.com/PyMesh/PyMesh.git && \
    cd PyMesh && \
    git submodule update --init && \
    python setup.py build && \
    python setup.py install && \
    cd .. && \
    rm -rf PyMesh /etc/profile.d/chroma_env.sh

CMD ["/bin/bash","-l"]
