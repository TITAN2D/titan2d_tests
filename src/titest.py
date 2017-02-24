import os
import sys
import inspect
import logging as log
from collections import OrderedDict

titan2d_tests_src_directory=os.path.abspath(os.path.join(os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))),"../src"))

if titan2d_tests_src_directory not in sys.path:
    sys.path.insert(0, titan2d_tests_src_directory)

from TitestCommon import titest_check_dir,run_command
from TitestConfig import TitestConfig
from TitestSrc import TitestGit
from TitestBuild import TitestBuild
from TitestSingleTest import run_single_test

import pprint

class Titest:
    def __init__(self):
        self.cfg=TitestConfig()
        self.build_results=None
    
    def check_top_test_dir(self):
        """check that top_test_dir is writable directory and create it if it does not exists and empty if needed"""
        if len(self.cfg.test_space_dir.split('/'))<=2:
            raise Exception("Bad choice of test_space_dir, too shallow!")
        titest_check_dir(self.cfg.test_space_dir,create=True);
        
        #remove respective directories if asked to redo
        if self.cfg.redo_src:
            if os.path.dirname(self.cfg.titan2d_src_dir)==self.cfg.test_space_dir:
                if os.path.exists(self.cfg.titan2d_src_dir):
                    run_command('rm -rf '+self.cfg.titan2d_src_dir,False)
            else:
                raise Exception("titan2d_src_dir (%s) is not in test_space_dir (%s). Can not redo it."%(self.cfg.titan2d_src_dir,self.cfg.test_space_dir))
        
        if self.cfg.redo_build:
            if os.path.dirname(self.cfg.build_dir)==self.cfg.test_space_dir:
                if os.path.exists(self.cfg.build_dir):
                    run_command('rm -rf '+self.cfg.build_dir,False)
            else:
                raise Exception("build_dir (%s) is not in test_space_dir (%s). Can not redo it."%(self.cfg.build_dir,self.cfg.test_space_dir))
            if os.path.dirname(self.cfg.install_dir)==self.cfg.test_space_dir:
                if os.path.exists(self.cfg.install_dir):
                    run_command('rm -rf '+self.cfg.install_dir,False)
            else:
                raise Exception("install_dir (%s) is not in test_space_dir (%s). Can not redo it."%(self.cfg.install_dir,self.cfg.test_space_dir))
        
        if self.cfg.redo_tests:
            if os.path.dirname(self.cfg.tests_dir)==self.cfg.test_space_dir:
                if os.path.exists(self.cfg.tests_dir):
                    run_command('rm -rf '+self.cfg.tests_dir,False)
            else:
                raise Exception("tests_dir (%s) is not in test_space_dir (%s). Can not redo it."%(self.cfg.tests_dir,self.cfg.test_space_dir))
        
        
    def get_src(self):
        log.info("Obtaining Titan2d source code")
        
        if self.cfg.titan2d_src=="git":
            TitestGit(self.cfg).get_src()
        else:
            raise Exception("Unknown way to get titan2d code: %s"%(str(self.cfg.titan2d_src),))
    
    def build(self):
        titest_build=TitestBuild(self.cfg)
        return titest_build.build()
    
    def run_tests(self):
        log.info("Running tests")
        
        #get tests to run
        if self.cfg.tests==None:
            log.info("There is not tests to perform")
            return None
        
        tests_to_run=[]
        
        asked_tests=self.cfg.tests.strip().split(",")
        for t in asked_tests:
            if os.path.isfile(os.path.join(self.cfg.titan2d_tests_topdir,"tests",t,"test.py")):
                #this is individual test
                tests_to_run.append((t,1))
            elif os.path.isfile(os.path.join(self.cfg.titan2d_tests_topdir,"tests",t)):
                #this should be file in format
                #test[:repeatitions]
                with open(os.path.join(self.cfg.titan2d_tests_topdir,"tests",t),"rt") as fin:
                    lines=fin.readlines()
                    for l in lines:
                        if len(l.strip())>0 and l.strip()[0]=="#":
                            continue
                        if len(l.strip())==0:
                            continue
                        v=l.strip().split(":")
                        if os.path.isfile(os.path.join(self.cfg.titan2d_tests_topdir,"tests",v[0],"test.py")):
                            if len(v)==1:
                                tests_to_run.append((v[0],1))
                            else:
                                tests_to_run.append((v[0],int(v[1])))
        print(tests_to_run)
        tests_results=OrderedDict()
        for testname,repeats in tests_to_run:
            if repeats==1:
                tests_results[testname]=run_single_test(self.cfg,testname)
            else:
                tests_results[testname]=[]
                for _ in range(repeats):
                    tests_results[testname].append(run_single_test(self.cfg,testname))
                
        log.info("Done running tests")
        return tests_results
        
    def run_from_cmdline(self):
        self.cfg.parse_cmdline_arg()
        log.info("Get following parameters:")
        log.info(str(self.cfg))
        
        self.check_top_test_dir()
        
        old_wd=os.getcwd()
        log.info("Changing working directory to test_space_dir(%s)"%(self.cfg.build_dir,))
        
        if self.cfg.run_src:
            self.get_src()
            
        if self.cfg.run_build:
            self.build_results=self.build()
        
        if self.cfg.run_tests:
            self.tests_results=self.run_tests()
        
        log.info("Done testing")
        log.info("Summary of results:")
        if self.cfg.run_build:
            log.info("Building:\n"+pprint.pformat(self.build_results,width=160))
        if self.cfg.run_tests:
            log.info("Testing:\n"+pprint.pformat(self.tests_results,width=160))
        os.chdir(old_wd)
        
        
    

if __name__ == '__main__':
    Titest().run_from_cmdline()