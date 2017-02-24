import os
import sys
import inspect
import logging as log

titan2d_tests_src_directory=os.path.abspath(os.path.join(os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))),"../src"))

if titan2d_tests_src_directory not in sys.path:
    sys.path.insert(0, titan2d_tests_src_directory)
    
class TitestConfig:
    def __init__(self):
        #Titest parameters
        #run code sources obtaining
        self.run_src=True
        #run build
        self.run_build=True
        #run tests
        self.run_tests=True
        #remove everything from top_test_dir and start from the beggining
        self.redo_all=False
        #redo code sources generation
        self.redo_src=False
        #redo build
        self.redo_build=False
        #redo tests
        self.redo_tests=False
        #remove some of files after successfull step
        self.cleanup=True
        
        #directories layout
        #top directory there building and testing will take place
        self.test_space_dir=None
        #directory for building
        self.build_dir=None
        #directory for tests
        self.tests_dir=None
        #directory for binaries installation
        self.install_dir=None
        #directory for titan2d source code
        self.titan2d_src_dir=None
        #top directory of titan2d_tests 
        self.titan2d_tests_topdir=os.path.dirname(titan2d_tests_src_directory)
        
        #source parameters
        self.titan2d_src="git"
        
        #building parameters
        #run autotools 
        self.run_autotools=True
        #which c++ compiler to use
        self.cxx=None
        #which c++ flags to use
        self.cxxflags=None
        #location of python binary
        self.python=None
        #location of swig top directory
        self.swig=None
        #compile with openmp support
        self.openmp=False
        #compile with mpi support
        self.mpi=False
        #compile with debug flags
        self.debug=False
        
        #titan2d dependencies
        #gdal top directory
        self.gdal=None
        #hdf5 top directory
        self.hdf5=None
        
        #run parameters
        #which titan binary to use
        self.titan_bin=None
        #which mpirun to use for mpi jobs
        self.mpirun=None
        #tests parameters
        self.binary_identical=False
        self.tests=None
        
    def set_top_test_dir(self,test_space_dir):
        self.test_space_dir=os.path.abspath(os.path.expanduser(test_space_dir))
        self.build_dir=os.path.join(self.test_space_dir,"build")
        self.install_dir=os.path.join(self.test_space_dir,"titan2d")
        self.tests_dir=os.path.join(self.test_space_dir,"tests")
        self.titan2d_src_dir=os.path.join(self.test_space_dir,"titan2d_src")
        
    def set_from_args(self,args):
        #Titest parameters
        self.redo_all=args.redo
        self.redo_src=args.redo_src
        self.redo_build=args.redo_build
        self.redo_tests=args.redo_tests
        if self.redo_all:
            self.redo_src=True
            self.redo_build=True
            self.redo_tests=True
        
        if args.run_src or args.run_build or args.run_tests:
            self.run_src=args.run_src
            self.run_build=args.run_build
            self.run_tests=args.run_tests
        else:
            self.run_src=True
            self.run_build=True
            self.run_tests=True
        self.cleanup=not args.no_prune
        #directories layout
        self.set_top_test_dir(args.test_space)
        
        #source parameters
        self.titan2d_src=args.src
        if isinstance(self.titan2d_src, str) and self.titan2d_src.lower()=="none":
            self.titan2d_src=None
        if self.titan2d_src!=None and self.titan2d_src!="git":
            raise Exception("for now only can get sources from github repo")
        if self.titan2d_src==None:
            #no sources no building
            self.titan2d_src_dir=None
            self.redo_src=False
            self.redo_build=False
            self.run_src=False
            self.run_build=False
            
        
        #building parameters
        self.run_autotools=not args.no_run_autotools
        self.cxx=args.cxx
        if self.cxx!=None:
            if self.cxx.count('/')>0:
                self.cxx=os.path.abspath(os.path.expanduser(self.cxx))
        self.cxxflags=args.cxxflags
        self.python=args.python
        self.swig=args.swig
        self.openmp=args.openmp
        self.mpi=args.mpi
        self.debug=args.debug
        
        #titan2d dependencies
        self.gdal=args.gdal
        self.hdf5=args.hdf5
        
        #run parameters
        self.mpirun=args.mpirun
        if self.cxx!=None and self.mpirun==None and self.cxx.count("mpi")>0:
            if self.cxx.count('/')>0:
                self.mpirun=os.path.join(os.path.dirname(self.cxx),"mpirun")
            else:
                self.mpirun="mpirun"
        self.titan_bin=args.titan_bin
        
        #tests parameters
        self.binary_identical=args.binary_identical
        self.tests=args.tests
        
        if self.titan_bin:
            #the titan binary is provide, so dont build it
            self.titan2d_src=None
            self.redo_src=False
            self.redo_build=False
            self.run_src=False
            self.run_build=False
            self.titan2d_src_dir=None
        else:
            self.titan_bin=os.path.join(self.install_dir,'bin','titan')
        
    def parse_cmdline_arg(self):
        """parse arguments provided through command line interface"""
        import argparse
        
        parser = argparse.ArgumentParser(description='Build Titan2D for tests')
    
        parser.add_argument('-ts', '--test-space', required=True, type=str,
            help="test space - directory where building and testing will be performed")
        
        parser.add_argument('-s', '--run_src', action='store_true', 
            help="obtain source code, if neither of -s, -b or -t set will run everything ")
        parser.add_argument('-b', '--run-build', action='store_true', 
            help="build binaries, if neither of -s, -b or -t set will run everything")
        parser.add_argument('-t', '--run-tests', action='store_true', 
            help="run tests")
        parser.add_argument('-r', '--redo', action='store_true', 
            help="redo build and tests, by default if build and tests was alread done whould not perform them")
        parser.add_argument('-rs', '--redo-src', action='store_true', 
            help="redo obtaining code sources")
        parser.add_argument('-rb', '--redo-build', action='store_true', 
            help="redo build")
        parser.add_argument('-rt', '--redo-tests', action='store_true',
            help="redo tests")
        parser.add_argument('-np', '--no-prune', action='store_true',
            help="do not remove some files, by default some files are deleted to save space")
        
        #source parameters
        parser.add_argument('-src', '--src', required=False, type=str, default='git',
            help="where to get titan2d sources if it is git will get it from git")
        
        #building parameters
        parser.add_argument('--no-run-autotools', action='store_true', default=False,
            help="do not run autotools")
        parser.add_argument('-cxx','--cxx', required=False, default=None,
            help="c++ compiler, if not set titan2d configure will use g++ from PATH")
        parser.add_argument('-cxxflags','--cxxflags', required=False, default=None,
            help="c++ flags, if not set titan2d configure will use default")
        parser.add_argument('-python', '--python', required=False, default=None,
            help="which python binary for titan2d, if not set titan2d configure will try to find it")
        parser.add_argument('-swig', '--swig', required=False, default=None,
            help="swig top directory for titan2d, if not set titan2d configure will try to find it")
        parser.add_argument('-openmp', '--openmp', action='store_true', 
            help="compile with openmp support")
        parser.add_argument('-mpi', '--mpi', action='store_true', 
            help="compile with mpi support")
        parser.add_argument('-debug', '--debug', action='store_true', 
            help="compile with debug flags")
        
        #titan2d dependencies
        parser.add_argument('-hdf5', '--hdf5',  required=False, default=None,
            help="hdf5 top directory for titan2d, if not set titan2d configure will try to find it")
        parser.add_argument('-gdal', '--gdal',  required=False, default=None,
            help="gdal top directory for titan2d, if not set titan2d configure will try to find it")
        
        #run parameters
        parser.add_argument('-bin', '--titan-bin',  required=False, default=None,
            help="specify titan binary. If set will just run tests (i.e. no source getting and no building)")
        parser.add_argument('-mpirun', '--mpirun',  required=False, default=None,
            help="mpirun for titan2d")
        
        #tests parameters
        parser.add_argument('-bi', '--binary-identical', action='store_true', default=False,
            help="perform binary identical comparison, i.e. tolerance is 0.0")
        
        parser.add_argument('-tests', '--tests',required=False, default="short",
            help="which tests to perform. Default: short.")
        
        parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
        
        args = parser.parse_args()
        
        if args.verbose:
            log.basicConfig(level=log.DEBUG,format='[%(asctime)s]-[%(levelname)s]: %(message)s')
        else:
            log.basicConfig(level=log.INFO,format='[%(asctime)s]-[%(levelname)s]: %(message)s')
    
        self.set_from_args(args)
        
        
    def __str__(self):
        #Titest parameters
        s=""
        s+="TitestConfig\n"
        s+="   Titest parameters\n"
        s+="\t remove everything from top_test_dir and start from the beggining: "+str(self.redo_all)+"\n"
        s+="\t run code sources obtaining: "+str(self.run_src)+"\n"
        s+="\t run build: "+str(self.run_build)+"\n"
        s+="\t run tests: "+str(self.run_tests)+"\n"
        s+="\t redo code sources generation: "+str(self.redo_src)+"\n"
        s+="\t redo build: "+str(self.redo_build)+"\n"
        s+="\t redo_tests: "+str(self.redo_tests)+"\n"
        s+="\t cleanup: "+str(self.cleanup)+"\n"
       

        s+="   Directories layout\n"
        s+="\t top directory there building and testing will take place: "+str(self.test_space_dir)+"\n"
        s+="\t directory for building: "+str(self.build_dir)+"\n"
        s+="\t directory for binaries installation: "+str(self.install_dir)+"\n"
        s+="\t directory for tests: "+str(self.tests_dir)+"\n"
        s+="\t directory for titan2d source code: "+str(self.titan2d_src_dir)+"\n"
        s+="\t top directory of titan2d_tests : "+str(self.titan2d_tests_topdir)+"\n"
        
        s+="\n"
        s+="\t where to get sources: "+str(self.titan2d_src)+"\n"
        
        s+="   building parameters\n"
        s+="\t run autotools : "+str(self.run_autotools)+"\n"
        s+="\t which c++ compiler to use: "+str(self.cxx)+"\n"
        s+="\t c++ flags: "+str(self.cxxflags)+"\n"
        s+="\t location of python binary: "+str(self.python)+"\n"
        s+="\t location of swig top directory: "+str(self.swig)+"\n"
        s+="\t compile with openmp support: "+str(self.openmp)+"\n"
        s+="\t compile with mpi support: "+str(self.mpi)+"\n"
        s+="\t compile with debug flags: "+str(self.debug)+"\n"
        
        s+="   titan2d dependencies\n"
        s+="\t gdal top directory: "+str(self.gdal)+"\n"
        s+="\t hdf5 top directory: "+str(self.hdf5)+"\n"

        s+="   run parameters\n"
        s+="\t titan binary to use: "+str(self.titan_bin)+"\n"
        s+="\t which mpirun to use for mpi jobs: "+str(self.mpirun)+"\n"
        
        s+="   tests parameters\n"
        s+="\t tests: "+str(self.tests)+"\n"
        return s
