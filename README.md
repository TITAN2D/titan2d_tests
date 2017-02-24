Installation of python for tests

Algthough currently titan2d uses python2.7 (we will move soon to python3) tests routines use python3.6

here is how to install python3.6 with anaconda:

conda create --name titan2d_tests_py36
source activate titan2d_tests_py36
conda install -c defaults python=3.6.0
conda install -c defaults h5py=2.6.0=np112py36_2


Building titan2d for tests

source activate titan2d_tests_py36



=running examples=

debug version, compiled with gnu compiler

python3 ~/titan_wsp/titan2d_tests/src/titest.py -ts ~/titan_wsp/tests/gcc_serial_nogui_git --python=/home/mikola/titan_wsp/regtests/dep_centos7/Python-2.7.9-gcc48/bin/python --swig=/home/mikola/titan_wsp/regtests/dep_centos7/swig-3.0.5-gcc48 --gdal=/home/mikola/titan_wsp/regtests/dep_centos7/gdal-1.10.1-gcc48 --hdf5=/home/mikola/titan_wsp/regtests/dep_centos7/hdf5-1.8.12-gcc48 --debug --cxxflags="-g -O0" -v -np --tests=short_omp

optimized, compiled with intel compiler

python3 ~/titan_wsp/titan2d_tests/src/titest.py -ts ~/titan_wsp/tests/iccopt_serial_nogui_git --python=/home/mikola/titan_wsp/regtests/dep_centos7/Python-2.7.9-gcc48/bin/python --swig=/home/mikola/titan_wsp/regtests/dep_centos7/swig-3.0.5-gcc48 --gdal=/home/mikola/titan_wsp/regtests/dep_centos7/gdal-1.10.1-gcc48 --hdf5=/home/mikola/titan_wsp/regtests/dep_centos7/hdf5-1.8.12-gcc48 --debug --cxxflags="-g -O3" -v -np --cxx=icpc --tests=short_omp

debug version, compiled with intel compiler

python3 ~/titan_wsp/titan2d_tests/src/titest.py -ts ~/titan_wsp/tests/icc_serial_nogui_git --python=/home/mikola/titan_wsp/regtests/dep_centos7/Python-2.7.9-gcc48/bin/python --swig=/home/mikola/titan_wsp/regtests/dep_centos7/swig-3.0.5-gcc48 --gdal=/home/mikola/titan_wsp/regtests/dep_centos7/gdal-1.10.1-gcc48 --hdf5=/home/mikola/titan_wsp/regtests/dep_centos7/hdf5-1.8.12-gcc48 --cxxflags="-g -O0" -debug -v -np --cxx=icpc --tests=short_omp -bi


