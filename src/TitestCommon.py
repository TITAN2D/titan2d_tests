import os
import sys
import inspect
import logging as log
import subprocess

titan2d_tests_src_directory=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if titan2d_tests_src_directory not in sys.path:
    sys.path.insert(0, titan2d_tests_src_directory)

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))),"../src")) )

def run_command(cmd,print_output=True,timeout=None,redirect_output=None):
    output=""
    try:
        if redirect_output is not None:
            cmd += " >& "+redirect_output

        output=subprocess.check_output(cmd, shell=True,executable="/bin/bash", timeout=timeout)
        output=str(output)
    except Exception as e:
        print('Error: Command '+cmd+' exit with error:')
        if print_output:
            print(output)
            if redirect_output is not None:
                with open(redirect_output, "rt") as fin:
                    print(fin.read())
        raise e
    else:
        if print_output:
            print(output)
        return output


def titest_check_dir(dirname, create=False):
    """check that dirname is writable directory and create it if it does not exists"""
    if os.path.exists(dirname) and not os.path.isdir(dirname):
        raise Exception("directory (%s) exists but is not directory"%(dirname,))
    
    if not os.path.isdir(dirname):
        if create:
            log.info("directory doesn't exist. Creating "+dirname)
            os.makedirs(dirname,mode=0o755)
        else:
            log.info("directory doesn't exist: "+dirname)
            raise Exception("directory doesn't exist: "+dirname)
    else:
        log.debug("directory (%s) exist."%(dirname,))
    
    if not (os.access(dirname, os.W_OK) and os.access(dirname, os.R_OK)):
        raise Exception("Can not read or write to directory: "+dirname)


class Titan2D_Conf:
    def __init__(self,args=None):
        self.debug=False
        self.python=None
        self.swig=None
        self.hdf5=None
        self.gdal=None
        if args:
            self.debug=args.debug
            self.python=args.python
            self.swig=args.swig
            self.hdf5=args.hdf5
            self.gdal=args.gdal

    
class TiTestConf:
    """stores location of repos"""
    def __init__(self,top_test_dir):
        self.top_test_dir=top_test_dir
        self.build_dir=os.path.join(self.top_test_dir,"build")
        self.install_dir=os.path.join(self.top_test_dir,"titan2d")
        
        self.titan2d_src_dir=None
        
        self.titan2d_tests_dir=os.path.dirname(titan2d_tests_src_directory)
    
    def check_top_test_dir(self, create=False):
        """check that top_test_dir is writable directory and create it if it does not exists"""
        titest_check_dir(self.top_test_dir,create);
    def check_build_dir(self,create=False):
        """check that build_dir is writable directory and create it if it does not exists"""
        titest_check_dir(self.build_dir,create);

def get_cpu_instructions_sets():
    """read instructions sets from /proc/cpuinfo"""
    flags=run_command('grep flags /proc/cpuinfo|head -n 1',False).split(':')[1].strip().split()
    return flags

titest_cmd_timing_format='/usr/bin/time -o timings -f \'{\"RealTime\":%e,\"RealTimeE\":\"%E\",\"UserTime\":%U,\"SysTime\":%S,\"MemoryMax\":%M}\' '   


        