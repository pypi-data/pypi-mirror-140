# parakeet
> **Parakeet** is a digital twin for cryo electron tomography and stands for **P**rogram for **A**nalysis and **R**econstruction of **A**rtificial data for **K**ryo **E**l**E**ctron **T**omography

![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/rosalindfranklininstitute/amplus-digital-twin.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/rosalindfranklininstitute/amplus-digital-twin/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/rosalindfranklininstitute/amplus-digital-twin.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/rosalindfranklininstitute/amplus-digital-twin/alerts/)
[![Building](https://github.com/rosalindfranklininstitute/amplus-digital-twin/actions/workflows/python-package.yml/badge.svg)](https://github.com/rosalindfranklininstitute/amplus-digital-twin/actions/workflows/python-package.yml)
[![Publishing](https://github.com/rosalindfranklininstitute/amplus-digital-twin/actions/workflows/python-publish.yml/badge.svg)](https://github.com/rosalindfranklininstitute/amplus-digital-twin/actions/workflows/python-publish.yml)
[![DOI](https://zenodo.org/badge/204956111.svg)](https://zenodo.org/badge/latestdoi/204956111)


## Installation

In order to build this package, the following dependencies are required:

- The CUDA toolkit
- FFTW

If you have multiple compiler versions or the compilers you want to use are not
automatically picked up by cmake, you can explicitly state the compiler
versions you would like to use as follows, where in this case we are using gcc
as the C++ compiler:

```sh
export CXX=${PATH_TO_CXX}/bin/g++
export CUDACXX=${PATH_TO_CUDA}/bin/nvcc
```

Depending on your GPU and the version of the CUDA toolkit you are using, it may
also be necessary to set the CMAKE_CUDA_ARCHITECTURES variable. This variable
is by default set to "OFF" in the CMakeLists.txt file which has the effect of
compiling CUDA kernels on the fly. If you have an old GPU, this may not work
and you will receive CUDA errors when attemping to run the simulations on the
GPU. In this case simply set the variable to the architecture supported by your
GPU as follows (the example below is for the compute_37 architecture):

```sh
export CMAKE_CUDA_ARCHITECTURES=37
```

To install from the github repository ensure you have the latest version of pip installed and do the following

```sh
python -m pip install git+https://github.com/rosalindfranklininstitute/amplus-digital-twin.git@master
```

To install from source, clone this repository. The repository has a submodule
for pybind11 so after cloning the repository run

```sh
git submodule update --init --recursive
```

Then do the following:

```sh
python -m pip install .
```

If you would like to run the tests then, clone this repository and then do the following:

```sh
python -m pip install .[test]
```

## Installation for developers

To install for development, clone this repository and then do the following:

```sh
python -m pip install -e .
```

## Testing

To run the tests, follow the installation instructions for developers and then do the following:

```sh
pytest
```

## Docker

Parakeet can also be installed and used via Docker (https://www.docker.com/get-started). To download parakeet's docker container you can do the following:

```sh
docker pull ghcr.io/rosalindfranklininstitute/parakeet:master
```

To use parakeet with docker with GPU support the host machine should have the approprate Nvidia drivers installed and docker needs to be installed with the nvidia container toolkit (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

To easily input and output data from the container the volume mechanism can be used, where a workspace directory of the host machine is mounted to a directory in the container (in the folder /mnt in the example below). For this reason it is advised that all the relevent files (e.g. config.yaml, sample.h5, etc.) should be present in the host workspace directory.

Below is an example on how to use parakeet with docker to simulate the exit wave:

```sh
docker run --gpus all -v $(pwd):/mnt --workdir=/mnt parakeet:master parakeet.simulate.exit_wave -c config.yaml -d gpu -s sample.h5 -e exit_wave.h5
```

## Singularity

Parakeet can also be installed and used via Singularity (https://sylabs.io/guides/2.6/user-guide/installation.html). To download parakeet's singularity container you can do the following:

```sh
singularity build parakeet.sif docker://gchr.io/rosalindfranklininstitute/parakeet:master
```

Again similar to docker, to use parakeet with singularity and GPU support, the host machine should have the approprate Nvidia drivers installed.

Below is an example on how to use parakeet with singularity to simulate the exit wave:

```sh
singularity run --nv parakeet.sif parakeet.simulate.exit_wave -c config_new.yaml -d gpu -s sample.h5 -e exit_wave.h5
```

## Usage

Simulation of datasets is split into a number of different commands. Each
command takes a set of command line options or a configuration file in YAML
format.

### Show default configuration

The default configuration parameters can be seen by typing the following
command:

```sh
parakeet.config.show
```

This will give some output like the following which can then be copied to a
yaml file (e.g. config.yaml):

```
Configuration:
    cluster:
        max_workers: 1
        method: null
    device: gpu
    microscope:
        beam:
            acceleration_voltage_spread: 8.0e-07
            drift: null
            electrons_per_angstrom: 30
            energy: 300
            energy_spread: 3.3e-07
        detector:
            dqe: true
            nx: 4000
            ny: 4000
            pixel_size: 1
        model: null
        objective_lens:
            c_10: 20000
            c_12: 0.0
            c_21: 0.0
            c_23: 0.0
            c_30: 2.7
            c_32: 0.0
            c_34: 0.0
            c_41: 0.0
            c_43: 0.0
            c_45: 0.0
            c_50: 0.0
            c_52: 0.0
            c_54: 0.0
            c_56: 0.0
            c_c: 2.7
            current_spread: 3.3e-07
            inner_aper_ang: 0.0
            m: 0
            outer_aper_ang: 0.0
            phi_12: 0.0
            phi_21: 0.0
            phi_23: 0.0
            phi_32: 0.0
            phi_34: 0.0
            phi_41: 0.0
            phi_43: 0.0
            phi_45: 0.0
            phi_52: 0.0
            phi_54: 0.0
            phi_56: 0.0
        phase_plate: false
    sample:
        box:
        - 4000
        - 4000
        - 4000
        centre:
        - 2000
        - 2000
        - 2000
        coords:
            filename: null
            recentre: false
        ice:
            density: 940
            generate: false
        molecules:
            4v1w: 0
            4v5d: 0
            6qt9: 0
        shape:
            cube:
                length: 4000
            cuboid:
                length_x: 4000
                length_y: 4000
                length_z: 4000
            cylinder:
                length: 10000
                radius: 1500
            type: cube
    scan:
        axis:
        - 0
        - 1
        - 0
        exposure_time: 1
        mode: still
        num_images: 1
        start_angle: 0
        start_pos: 0
        step_angle: 10
        step_pos: auto
    simulation:
        division_thickness: 100
        ice: false
        margin: 100
        padding: 100
        slice_thickness: 3.0
```

### Generate sample model

Once the configuration file has been generated a new sample file can be created
with the following command:

```sh
parakeet.sample.new -c config.yaml
```

This will result in a file "sample.h5" being generated. This file contains
information about the size and shape of the sample but as yet doesn't contain
any atomic coordinates. The atomic model is added by running the following
command which adds molecules to the sample file. If a single molcule is
specified then it will be placed in the centre of the sample volume. If
multiple molecules are specified then the molecules will be positioned at
random locations in the sample volume. This command will update the "sample.h5"
file with the atomic coordinates but will not generated any new files.

```sh
parakeet.sample.add_molecules -c config.yaml
```

### Simulate EM images

Once the atomic model is ready, the EM images can be simulated with the
following commands. Each stage of the simulation is separated because it may be
desirable to simulate many different defocused images from the sample exit wave
for example or many different doses for the sample defocusses image. Being
separate, the output of one stage can be reused for multiple runs of the next
stage. The first stage is to simulate the exit wave. This is the propagation
of the electron wave through the sample. It is therefore the most
computationally intensive part of the processes since the contribution of all
atoms within the sample needs to be calculated.


```sh
parakeet.simulate.exit_wave -c config.yaml
```

This command will generate a file "exit_wave.h5" which will contain the exit
wave of all tilt angles. The next step is to simulate the micropscope optics
which is done with the following command:

```sh
parakeet.simulate.optics -c config.yaml
```

This step is much quicker as it only scales with the size of the detector image
and doesn't require the atomic coordinates again. The command will output a
file "optics.h5". Finally, the response of the detector can be simulated with
the following command:

```sh
parakeet.simulate.image -c config.yaml
```

This command will add the detector DQE and the Poisson noise for a given dose
and will output a file "image.h5".

### Other functions

Typically we cant to output an MRC file for further processing. The hdf5 files
can easily be exported to MRC by the following command:

```sh
parakeet.export file.h5 -o file.mrc
```

The export command can also be used to rebin the image or select a region of interest. 

## Documentation

Checkout the [documentation](https://rosalindfranklininstitute.github.io/amplus-digital-twin/) for more information!

## Issues

Please use the [GitHub issue tracker](https://github.com/rosalindfranklininstitute/parakeet/issues) to submit bugs or request features.

## License

Copyright Diamond Light Source and Rosalind Franklin Institute, 2019.

Distributed under the terms of the GPLv3 license, parakeet is free and open source software.

