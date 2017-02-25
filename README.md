# Titan2d-Tests: Tests for Titan2d

Titan2d-Tests compiles and run tests for Titan2d.

## Prerequirements for Titan2d-Tests

### Installation of python for tests

Algthough currently titan2d uses python2.7 (we will move soon to python3) tests routines use python3.6

here is how to install python3.6 with anaconda:

```bash
conda create --name titan2d_tests_py36
source activate titan2d_tests_py36
conda install -c defaults python=3.6.0
conda install -c defaults h5py=2.6.0=np112py36_2
```

## Running Titan2d-Tests

titest.py is the main utility to run Titan2d-Tests. It obtains source code,
compile it and run tests

```bash
source activate titan2d_tests_py36

python3 ~/titan_wsp/titan2d_tests/src/titest.py --test-space=~/titan_wsp/tests/gcc_serial_nogui_git 

```

### titest.py: Command Line Arguments

Command line arguments for titest.py can be separated into several group:

* Titest parameters - defines the behaiviour of titest.py

* Directories layout

* Sources location
        
* Building parameters - parameters passed to configure of titan2d, if something is not set it do not specify it for configure as well

* titan2d dependencies

* run parameters

* tests parameters


Bellow is help text from titest.py

```
usage: titest.py [-h] -ts TEST_SPACE [-s] [-b] [-t] [-r] [-rs] [-rb] [-rt]
                 [-np] [-src SRC] [--no-run-autotools] [-cxx CXX]
                 [-cxxflags CXXFLAGS] [-python PYTHON] [-swig SWIG] [-openmp]
                 [-mpi] [-debug] [-hdf5 HDF5] [-gdal GDAL] [-bin TITAN_BIN]
                 [-mpirun MPIRUN] [-bi] [-tests TESTS] [-v]

Build Titan2D for tests

optional arguments:
  -h, --help            show this help message and exit
  -ts TEST_SPACE, --test-space TEST_SPACE
                        test space - directory where building and testing will
                        be performed
  -s, --run_src         obtain source code, if neither of -s, -b or -t set
                        will run everything
  -b, --run-build       build binaries, if neither of -s, -b or -t set will
                        run everything
  -t, --run-tests       run tests
  -r, --redo            redo build and tests, by default if build and tests
                        was alread done whould not perform them
  -rs, --redo-src       redo obtaining code sources
  -rb, --redo-build     redo build
  -rt, --redo-tests     redo tests
  -np, --no-prune       do not remove some files, by default some files are
                        deleted to save space
  -src SRC, --src SRC   where to get titan2d sources if it is git will get it
                        from git
  --no-run-autotools    do not run autotools
  -cxx CXX, --cxx CXX   c++ compiler, if not set titan2d configure will use
                        g++ from PATH
  -cxxflags CXXFLAGS, --cxxflags CXXFLAGS
                        c++ flags, if not set titan2d configure will use
                        default
  -python PYTHON, --python PYTHON
                        which python binary for titan2d, if not set titan2d
                        configure will try to find it
  -swig SWIG, --swig SWIG
                        swig top directory for titan2d, if not set titan2d
                        configure will try to find it
  -openmp, --openmp     compile with openmp support
  -mpi, --mpi           compile with mpi support
  -debug, --debug       compile with debug flags
  -hdf5 HDF5, --hdf5 HDF5
                        hdf5 top directory for titan2d, if not set titan2d
                        configure will try to find it
  -gdal GDAL, --gdal GDAL
                        gdal top directory for titan2d, if not set titan2d
                        configure will try to find it
  -bin TITAN_BIN, --titan-bin TITAN_BIN
                        specify titan binary. If set will just run tests (i.e.
                        no source getting and no building)
  -mpirun MPIRUN, --mpirun MPIRUN
                        mpirun for titan2d
  -bi, --binary-identical
                        perform binary identical comparison, i.e. tolerance is
                        0.0
  -tests TESTS, --tests TESTS
                        which tests to perform. Default: short
  -v, --verbose         turn on verbose logging
```

## Examples

debug version, compiled with gnu compiler

```bash
python3 ~/titan_wsp/titan2d_tests/src/titest.py -ts ~/titan_wsp/tests/gcc_serial_nogui_git \
--python=/home/mikola/titan_wsp/regtests/dep_centos7/Python-2.7.9-gcc48/bin/python \
--swig=/home/mikola/titan_wsp/regtests/dep_centos7/swig-3.0.5-gcc48 \
--gdal=/home/mikola/titan_wsp/regtests/dep_centos7/gdal-1.10.1-gcc48 \
--hdf5=/home/mikola/titan_wsp/regtests/dep_centos7/hdf5-1.8.12-gcc48 \
--debug --cxxflags="-g -O0" -v -np --tests=short_omp
```

optimized, compiled with intel compiler

```bash
python3 ~/titan_wsp/titan2d_tests/src/titest.py -ts ~/titan_wsp/tests/iccopt_serial_nogui_git \
--python=/home/mikola/titan_wsp/regtests/dep_centos7/Python-2.7.9-gcc48/bin/python \
--swig=/home/mikola/titan_wsp/regtests/dep_centos7/swig-3.0.5-gcc48 \
--gdal=/home/mikola/titan_wsp/regtests/dep_centos7/gdal-1.10.1-gcc48 \
--hdf5=/home/mikola/titan_wsp/regtests/dep_centos7/hdf5-1.8.12-gcc48 \
--debug --cxxflags="-g -O3" -v -np --cxx=icpc --tests=short_omp
```

debug version, compiled with intel compiler

```bash
python3 ~/titan_wsp/titan2d_tests/src/titest.py -ts ~/titan_wsp/tests/icc_serial_nogui_git \
--python=/home/mikola/titan_wsp/regtests/dep_centos7/Python-2.7.9-gcc48/bin/python \
--swig=/home/mikola/titan_wsp/regtests/dep_centos7/swig-3.0.5-gcc48 \
--gdal=/home/mikola/titan_wsp/regtests/dep_centos7/gdal-1.10.1-gcc48 \
--hdf5=/home/mikola/titan_wsp/regtests/dep_centos7/hdf5-1.8.12-gcc48 \
--cxxflags="-g -O0" -debug -v -np --cxx=icpc --tests=short_omp -bi
```

