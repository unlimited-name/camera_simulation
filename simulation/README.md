# Simulation using Python pack: chroma

## Overview
This repository is the code used in camera view simulation of SBC Argon chamber. In this page we are going to briefly explain how to reproduce the results. There is also a detailed explanation file in `/Archived/guide.pdf`. Simulation in chroma resembles that in Geant4 a lot, so it is very helpful to read or run a Geant4 example before using chroma. 

## Prerequisite
[Chroma](https://github.com/BenLand100/chroma) is a python-based GPU photon simulation pack, which works particularly on Linux platform. The easiest way to run it in a Linux machine is using [docker](https://www.docker.com/) to pull the image provided by the maintainer of chroma. 

For Windows and macOS users, we have a roundabout way: install and use chroma in a Linux virtual machine on cloud platforms. (Note you cannot setup a Linux machine and then use docker, at least at the time when I wrote this.) Refer to the [installation](https://github.com/unlimited-name/installation) repository for details. 

## Geometry
The code for geometry construction is written in `detector_construction.py`. We include most of the bulk materials and reflectors (those releted to optics inside the chamber) inside the pressure vessel. The genre of writing the geometry could be referred to the Geant4 geometry in [SBC Geant4 repository](https://github.com/SBC-Collaboration/sbcGEANT4). 

Chroma uses surface model, which means geometry objects are made of meshes. You will need to prepare meshes for every object in geometry construction. Freedom is allowd in meshing, you may choose whatever method but make sure you check the definition of surface and normal vector in chroma [whitebook](https://github.com/BenLand100/chroma/blob/master/doc/source/chroma.pdf). I used [pymesh](https://pymesh.readthedocs.io/en/latest/) for mesh generation. The meshes and corresponding code are inside the folder `/Meshes`

## Table of files
+ illumination.py

The code for first step of simulation. Run and save an illumination_map.npy.

+ simulation.py

The code for second step of simulation. Require an illumination_map.npy, and will produce a 2d ndarray of light intensity. Use `plt.imshow()` to generate the image. 

+ simulation_old.py

An initial version of simulation code. Light source and geometry construction could be interactively written if needed. 

+ add_reflection.py

The code to add reflection into illumination_map. Please note, merely adding in the map is not enough: you need to be able to detect the "reflection" in geometry.

+ photon_track.py

A simulation used to run and plot the track of photons generated by a light source. Making use of it might help you investigate your own light source. 

+ source.py

Stores different kinds of self-defined light source functions. To write a new function of your own, follow the examples in this file. 

+ optics.py

An important file for simulation: records the optical properties of self-defined bulk material and surface materials. Adjust the data (e.g. the absorption rate of reflectors) locally to change simulation setup. 

+ mathematics.py

Used to store the math tools in simulation. 

+ Archived (folder)

This folder is used to store out-dated files and should be ignored. One exception is `/Archived/LED_list_generation.py`, which is the file uesd to generate LED light source, and the corresponding `led_list.npy` is still used. 

+ Tests (folder)

This folder is uesd to store some simple test scripts. In every script, read comments in the beginning to find out what it does.


## To be continued...