import os
import sys
import logging as log
import shutil
import traceback
import re
import pprint

from TitestCommon import titest_check_dir,run_command,get_cpu_instructions_sets,titest_cmd_timing_format
from collections import OrderedDict
from compare_restart_hdf5 import compare_restart_hdf5
from compare_visout_hdf5 import compare_vizout_hdf5
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
        
        self.err_tolerance={
            'h':1.0e-08 if not self.cfg.binary_identical else 0.0,
            'hVx':1.0e-08 if not self.cfg.binary_identical else 0.0,
            'hVy':1.0e-08 if not self.cfg.binary_identical else 0.0,
            'max_kinergy':1.0e-08 if not self.cfg.binary_identical else 0.0,
            'max_pileheight':1.0e-08 if not self.cfg.binary_identical else 0.0
        }
        
        self.err_visout_tolerance={
            'Pile_Height':1.0e-08,
            'XMomentum':1.0e-08,
            'YMomentum':1.0e-08
        }
        
        self.err_outline_tolerance={
            'maxkerecord':1.0e-08,
            'maxpileheightrecord':1.0e-08
        }
        
        
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
        loc_ref_dir=os.path.join(self.runtest_dir,"ref")
        
        restart_h5_to_comp=[]
        xdmf_h5_to_comp=[]
        maxkerecord_to_comp=[]
        pileheightrecord_to_comp=[]
        message=""
        #find what we can to compare
        for f in os.listdir(loc_ref_dir):
            if os.path.join(loc_ref_dir,f):
                #see do we have vizout to compare
                if re.match(r"snapshot_p\d+_i\d+\.h5", f):
                    restart_h5_to_comp.append(f)
                if re.match(r"xdmf_p\d+_i\d+\.h5", f):
                    xdmf_h5_to_comp.append(f)
                if re.match(r"maxkerecord.[-0-9]+", f):
                    maxkerecord_to_comp.append(f)
                if re.match(r"pileheightrecord.[-0-9]+", f):
                    pileheightrecord_to_comp.append(f)
        restart_h5_to_comp=sorted(restart_h5_to_comp)
        log.debug("restart_h5_to_comp: "+" ".join(restart_h5_to_comp))
        self.results["restart"]=OrderedDict()
        for restart_h5 in restart_h5_to_comp:
            self.results["restart"][restart_h5]=compare_restart_hdf5(
                os.path.join(self.runtest_dir,'restart',restart_h5),
                os.path.join(loc_ref_dir,restart_h5)
            )
            
        xdmf_h5_to_comp=sorted(xdmf_h5_to_comp)
        log.debug("xdmf_h5_to_comp: "+" ".join(xdmf_h5_to_comp))
        self.results["visout"]=OrderedDict()
        for xdmf_h5 in xdmf_h5_to_comp:
            self.results["visout"][xdmf_h5]=compare_vizout_hdf5(
                os.path.join(self.runtest_dir,'vizout',xdmf_h5),
                os.path.join(loc_ref_dir,xdmf_h5)
            )
        log.debug("maxkerecord_to_comp: "+" ".join(maxkerecord_to_comp))
        self.results["maxkerecord"]=OrderedDict()
        for f in maxkerecord_to_comp:
            self.results["maxkerecord"][f]=compare_maxpilehights(
                    os.path.join(self.runtest_dir,f),
                    os.path.join(loc_ref_dir,f)
                )
        log.debug("pileheightrecord_to_comp: "+" ".join(pileheightrecord_to_comp))
        self.results["maxpileheightrecord"]=OrderedDict()
        for f in pileheightrecord_to_comp:
            self.results["maxpileheightrecord"][f]=compare_maxpilehights(
                    os.path.join(self.runtest_dir,f),
                    os.path.join(loc_ref_dir,f)
                )
        
        #find did we pass the test
        passed=True
        should_have_same_elements=self.cfg.binary_identical
        
        for restart_filename,restart in self.results["restart"].items():
            for field in ['h','hVx','hVy','max_kinergy','max_pileheight']:
                this_test_passed=None
                tolerance=self.err_tolerance[field]
                
                if field not in restart:
                    this_test_passed=False
                    message+="Field %s is not present in restart file (%s) analysis output\n"%(field,restart_filename,)
                    
                if this_test_passed!=False and 'Comparable' not in restart[field]:
                    this_test_passed=False
                    message+="Field Comparable is not present in restart file (%s) analysis output\n"%(restart_filename,)
                
                if this_test_passed!=False and 'Err' not in restart[field]:
                    this_test_passed=False
                    message+="Field Err is not present in restart file (%s) analysis output\n"%(restart_filename,)
                
                if this_test_passed!=False:
                    if restart[field]['Comparable']:
                        if restart[field]['Err']<=tolerance:
                            #passed
                            this_test_passed=True
                        else:
                            #didn't pass
                            this_test_passed=False
                            message+="%s do not satisfy tollerance (%f > %f)\n"%(field,restart[field]['Err'],tolerance)
                    else:
                        if should_have_same_elements:
                            this_test_passed=False
                        elif field in ['max_kinergy','max_pileheight']:
                            #if should_have_same_elements==False and field is outline
                            if restart[field]['Err']<=tolerance:
                                #passed
                                this_test_passed=True
                            else:
                                #didn't pass
                                this_test_passed=False
                                message+="%s do not satisfy tollerance (%f > %f)\n"%(field,restart[field]['Err'],tolerance)
                        else:
                            this_test_passed=None
                
                restart[field]['passed']=this_test_passed
                if this_test_passed!=None:
                    passed=passed and this_test_passed
        
        if len(self.results["restart"])>0:
            self.results['passed']=passed
        
        for _,visout in self.results["visout"].items():
            try:
                Comparable=True
                if not ('ElementsNumberIsSame' in visout and visout['ElementsNumberIsSame']):
                    Comparable=False
                if not ('PointsNumberIsSame' in visout and visout['PointsNumberIsSame']):
                    Comparable=False
                if not ('PointsRMSD' in visout and visout['PointsRMSD']==0.0):
                    Comparable=False
                if not ('ConnectionsIsSame' in visout and visout['ConnectionsIsSame']):
                    Comparable=False
                
                this_test_passed=None
                if Comparable==False:
                    if should_have_same_elements:
                        this_test_passed=False
                    else:
                        this_test_passed=None
                else:
                    for field in ['Pile_Height','XMomentum','YMomentum']:
                        tolerance=self.err_visout_tolerance[field]
                        if visout[field+'_Err']<=tolerance:
                            #passed
                            this_test_passed=True
                        else:
                            #didn't pass
                            this_test_passed=False
            except Exception as e:
                log.info("Something went wrong during visout analysis")
                traceback.print_exc()
                this_test_passed=False
                message+="Something went wrong during visout analysis\n"
            
            visout['passed']=this_test_passed
            if visout['passed']!=None:
                passed=passed and visout['passed']
                    #if should_have_same_elements
        
        for _,maxkerecord in self.results["maxkerecord"].items():
            try:
                this_test_passed=maxkerecord['Err']<=self.err_outline_tolerance['maxkerecord']
            except Exception as _:
                log.info("Something went wrong during maxkerecord analysis")
                traceback.print_exc()
                this_test_passed=False
                message+="Something went wrong during maxkerecord analysis\n"
            
            maxkerecord['passed']=this_test_passed
            if maxkerecord['passed']!=None:
                passed=passed and maxkerecord['passed']
        
        for _,maxpileheightrecord in self.results["maxkerecord"].items():
            try:
                this_test_passed=maxpileheightrecord['Err']<=self.err_outline_tolerance['maxpileheightrecord']
            except Exception as _:
                log.info("Something went wrong during maxpileheightrecord analysis")
                traceback.print_exc()
                this_test_passed=False
                message+="Something went wrong during maxpileheightrecord analysis\n"
            
            maxpileheightrecord['passed']=this_test_passed
            if maxpileheightrecord['passed']!=None:
                passed=passed and maxpileheightrecord['passed']
        
        if len(self.results["restart"])==0:
            self.results['passed']=passed
        
        if message!=None:
            self.results['message']=message
    
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
        #check can this test be run
        if self.threads>1 and self.cfg.openmp==False:
            return OrderedDict([
                ('passed',None),
                ('message',"This is multi-thread test but titan2d compiled without openmp support")
            ])
        if self.mpi_procs!=None and self.mpi_procs>1 and self.cfg.mpi==False:
            return OrderedDict([
                ('passed',None),
                ('message',"This is multi-MPI-processes test but titan2d compiled without MPI support")
            ])
        
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
        
        os.chdir(self.runtest_dir)
        with open("results","at") as fout:
            fout.write(pprint.pformat(self.results,width=160)+",\n")
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
    try:
        results=this_test.run()
    except Exception as e:
            log.info("The test failed")
            traceback.print_exc()
            results=OrderedDict([
                ('passed',False),
                ('message',str(e))
            ])
    
    os.chdir(old_wd)
    log.info("Done running test: %s"%(testname,))
    return results
