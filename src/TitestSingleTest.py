import os
import sys
import logging as log
import shutil
import traceback
import re

from TitestCommon import titest_check_dir,run_command,get_cpu_instructions_sets,titest_cmd_timing_format
from collections import OrderedDict
from compare_hdf5 import compare_vizout_hdf5
from compare_maxpilehights import compare_maxpilehights

class TitestSingleTest:
    """base class for single titan run test"""
    def __init__(self,cfg,testname):
        self.cfg=cfg
        self.testname=testname
        self.test_dir=os.path.join(self.cfg.titan2d_tests_topdir,'tests',self.testname)
        self.runtest_dir=os.path.join(self.cfg.test_space_dir,'tests',self.testname)
        
        #input directiry files from there will be copied to runtest_dir
        self.input_dir='input'
        #number of threads
        self.threads=1
        #number of MPI processes
        self.mpi_procs=None
        #timeout for test in seconds
        self.timeout=30*60
        #directory with reference results for comparison
        self.ref_dir="ref"
        #reference computer architechture to compare with
        self.ref_arch="std"
        if "fma" in get_cpu_instructions_sets():
            self.ref_arch="fma"
    
        #file to not remove during clean-up
        self.files_to_keep=[
            'input.py',
            'results',
            'timings',
            'run.out',
            'ref',
            'failed'
            ]
        self.results=OrderedDict([("passed",None)])
        
    def prolog(self):
        self.old_wd=os.getcwd()
        
    def epilog(self):
        os.chdir(self.old_wd)
        del self.old_wd
        
    def copy_and_link_input(self):
        #copy input files
        run_command('cp -r '+os.path.join(self.test_dir,self.input_dir)+"/* "+self.runtest_dir+'/')
        #link reference
        os.symlink(os.path.join(self.test_dir,self.ref_dir,self.ref_arch),os.path.join(self.runtest_dir,"ref"))
    
    def patch_script_with_titan2d_tests_topdir(self):
        """replace LOCATION_OF_TITAN2D_TESTS in input.py with self.cfg.titan2d_tests_topdir"""
        if os.path.exists(os.path.join(self.runtest_dir,'input.py')):
            run_command('sed -i "s|LOCATION_OF_TITAN2D_TESTS|'+self.cfg.titan2d_tests_topdir+'|g" input.py')
    
    def run_titan(self):
        """run titan"""
        execution_command=""
        if self.mpi_procs!=None and self.mpi_procs>1:
            execution_command+=self.cfg.mpirun+" -n "+str(self.mpi_procs)+" "
            
        execution_command+=self.cfg.titan_bin
        
        if self.threads > 1:
            execution_command+=" -nt %d"%(self.threads,)
        execution_command+=" input.py"
        
        log.debug("Running command: "+execution_command)
        
        run_cmd=titest_cmd_timing_format+' '+execution_command+" >& run.out"
        run_command(run_cmd,False,self.timeout)
        
    def read_timings(self):
        try:
            with open("timings","r") as fin:
                timings_str=fin.read()
                timings=eval(timings_str)
            self.results["timing"]=OrderedDict([
                ('RealTime',timings['RealTime']),
                ('RealTimeE',timings['RealTimeE']),
                ('UserTime',timings['UserTime']),
                ('SysTime',timings['SysTime']),
                ('MemoryMax',timings['MemoryMax'])
            ])
        except Exception as e:
            with open(os.path.join(self.runtest_dir,'failed'), 'w'):
                pass
            log.info("This test failed")
            traceback.print_exc()
            
            raise e
        
    def analyze_results(self):
        """analyze the results of titan run"""
        binary_identical_test=False
        if self.cfg.binary_identical:
            binary_identical_test=True
        
        loc_ref_dir=os.path.join(self.runtest_dir,"ref")
        
        xdmf_h5_to_comp=[]
        maxkerecord_to_comp=[]
        pileheightrecord_to_comp=[]
        #find what we can to compare
        for f in os.listdir(loc_ref_dir):
            if os.path.join(loc_ref_dir,f):
                #see do we have vizout to compare
                if re.match(r"xdmf_p\d+_i\d+\.h5", f):
                    xdmf_h5_to_comp.append(f)
                if re.match(r"maxkerecord.[-0-9]+", f):
                    maxkerecord_to_comp.append(f)
                if re.match(r"pileheightrecord.[-0-9]+", f):
                    pileheightrecord_to_comp.append(f)
        xdmf_h5_to_comp=sorted(xdmf_h5_to_comp)
        log.debug("xdmf_h5_to_comp: "+" ".join(xdmf_h5_to_comp))
        
        if binary_identical_test:
            for xdmf_h5 in xdmf_h5_to_comp:
                xdmf_h5_name=xdmf_h5 if len(xdmf_h5_to_comp)>1 else "visout"
                self.results[xdmf_h5_name]=compare_vizout_hdf5(
                    os.path.join(self.runtest_dir,'vizout',xdmf_h5),
                    os.path.join(loc_ref_dir,xdmf_h5)
                )
        log.debug("maxkerecord_to_comp: "+" ".join(maxkerecord_to_comp))
        for f in maxkerecord_to_comp:
            f_name=f if len(maxkerecord_to_comp)>1 else "maxkerecord"
            self.results[f_name]=compare_maxpilehights(
                    os.path.join(self.runtest_dir,f),
                    os.path.join(loc_ref_dir,f)
                )
        log.debug("pileheightrecord_to_comp: "+" ".join(pileheightrecord_to_comp))
        for f in pileheightrecord_to_comp:
            f_name=f if len(pileheightrecord_to_comp)>1 else "pileheightrecord"
            self.results[f_name]=compare_maxpilehights(
                    os.path.join(self.runtest_dir,f),
                    os.path.join(loc_ref_dir,f)
                )
        #find did we pass the test
        passed=True
        self.results['passed']=passed
        
        
            
    
    def cleanup(self):
        """remove most of files from titan run, should be called in case of successfull test"""
        def clean_dir(dirname,files_to_keep):
            for filename in os.listdir(dirname):
                full_filename=os.path.join(dirname, filename)
                if os.path.isdir(full_filename) and not os.path.islink(full_filename):
                    clean_dir(full_filename,files_to_keep)
                    if len(os.listdir(full_filename))==0:
                        os.rmdir(full_filename)
                else:
                    if (os.path.isfile(full_filename) or os.path.islink(full_filename)) and (filename not in files_to_keep):
                        os.remove(full_filename)
        
        clean_dir(self.runtest_dir,self.files_to_keep)
        
    
    def run(self):
        self.prolog()
        log.debug("run test directory: "+self.runtest_dir)
        self.results['passed']=False
        
        if os.path.exists(self.runtest_dir):
            log.debug("run test directory exists, cleanup it: "+self.runtest_dir)
            self.cleanup()
            if os.path.exists(os.path.join(self.runtest_dir,"ref")):
                os.remove(os.path.join(self.runtest_dir,"ref"))
            if os.path.exists(os.path.join(self.runtest_dir,"failed")):
                os.remove(os.path.join(self.runtest_dir,"failed"))
                
        titest_check_dir(self.runtest_dir,create=True)
        
        os.chdir(self.runtest_dir)
        
        self.copy_and_link_input()
        
        self.patch_script_with_titan2d_tests_topdir()
        
        self.run_titan()
        
        self.read_timings()
        
        self.analyze_results()
        
        if self.cfg.cleanup:
            self.cleanup()
        
        self.epilog()
        return self.results
    
    
        

def run_single_test(cfg,testname):
    log.info("Running test: %s"%(testname,))
    this_test_py=os.path.join(cfg.titan2d_tests_topdir,'tests',testname,"test.py")
    if not os.path.isfile(this_test_py):
        raise Exception("Script file for this test do not exists (%s)"%(this_test_py,))
    
    this_test_py_vars={}
    exec(open(this_test_py,"r").read(),this_test_py_vars)
    if 'ThisTest' not in this_test_py_vars:
        raise Exception("There is no ThisTest class in %s"%(this_test_py,))
    
    old_wd=os.getcwd()
    
    run_all_tests_dir=os.path.join(cfg.test_space_dir,'tests')
    
    titest_check_dir(run_all_tests_dir,create=True)
    
    os.chdir(run_all_tests_dir)
    
    this_test=this_test_py_vars['ThisTest'](cfg,testname)
    results=this_test.run()
    #TitestSingleTest(cfg,testname).run()
    
    os.chdir(old_wd)
    log.info("Done running test: %s"%(testname,))
    return results
