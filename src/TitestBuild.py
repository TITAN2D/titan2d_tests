import os
import logging as log
from collections import OrderedDict
import traceback
import pprint
from TitestCommon import run_command,titest_check_dir


from timeit import default_timer as timer

class TitestBuild:
    """class for titan2d builders"""
    def __init__(self, cfg):
        self.cfg=cfg
        
        self.successfull_build=False
        #init results
        self.results=OrderedDict([
            #was the titan binary made
            ('passed',None),
            ('message',""),
            #specify was it complete build or incremental
            ('complete_build',None),
            #configure command line
            ('configure_command',None),
            #time to run configure
            ('configure_timing',None),
             #time to run make -j
            ('make_timing',None),
            #time to run make -j install
            ('make_install_timing',None),
            #time to run make clean
            ('make_clean_timing',None)       
        ])
        
        
    def check_build_dir(self, create=False):
        titest_check_dir(self.cfg.build_dir,create)
    
    def _get_configure_flags(self):
        "get configure flags other than --prefix"
        cfg=self.cfg
        flags=""
        
        if cfg.debug:
            flags+=" --enable-debug"
        if cfg.openmp:
            flags+=" --enable-openmp"
        if cfg.mpi:
            flags+=" --enable-mpi"
            
        flags+=" --disable-java-gui"
        
        if cfg.cxx:
            flags+=" CXX="+cfg.cxx
        if cfg.cxxflags:
            flags+=' CXXFLAGS="'+cfg.cxxflags+'"'
        if cfg.python:
            flags+=" PYTHON="+cfg.python
        if cfg.swig:
            flags+=" --with-swig="+cfg.swig
        
        if cfg.gdal:
            flags+=" --with-gdal="+cfg.gdal
        if cfg.hdf5:
            flags+=" --with-hdf5="+cfg.hdf5
        
        return flags
    
    def _configure(self):
        if self.cfg.redo_build==False:
            if os.path.exists(os.path.join(self.cfg.build_dir,'Makefile')):
                log.info("Configure was ran before, would not run it now")
                self.results['complete_build']=False
                return
                
        old_wd=os.getcwd()
        
        os.chdir(self.cfg.build_dir)
        

        log.info("Running configure")
        configure=self.cfg.titan2d_src_dir+"/configure "
        configure+="--prefix="+self.cfg.install_dir
        configure+=" "+self._get_configure_flags()
        self.results['configure_command']=configure
        log.info('Configure command: '+configure)
        
        start = timer()
        run_command(configure+' >& configure.out',False)
        self.results['configure_timing']=timer()-start
        
        if not os.path.exists(os.path.join(self.cfg.build_dir,'Makefile')):
            raise Exception("Can not configure")
        
        os.chdir(old_wd)
    
    def _make(self):
        old_wd=os.getcwd()
        log.info("Running make")
        os.chdir(self.cfg.build_dir)
        
        start = timer()
        run_command('make -j >& make.log',False)
        self.results['make_timing']=timer()-start
        
        os.chdir(old_wd)
        
        if not os.path.exists(os.path.join(self.cfg.build_dir,'src','main','titan')):
            raise Exception("Can not build")
        
    
    def _make_install(self):
        old_wd=os.getcwd()
        log.info("Running make install")
        os.chdir(self.cfg.build_dir)
        
        start = timer()
        run_command('make -j install >& make_install.log',False)
        self.results['make_install_timing']=timer()-start
                
        os.chdir(old_wd)
        
        if not os.path.exists(os.path.join(self.cfg.install_dir,'bin','titan')):
            raise Exception("Can not install")
        else:
            self.successfull_build=True
    
    def _cleanup(self):
        old_wd=os.getcwd()
        log.info("Running make clean")
        os.chdir(self.cfg.build_dir)
        
        start = timer()
        run_command('make -j clean >& make_clean.log',False)
        self.results['make_clean_timing']=timer()-start
                
        os.chdir(old_wd)
    
        
    def build(self):
        log.info("Building Titan2d")
        old_wd=os.getcwd()
        try:
            self.check_build_dir(create=True)
    
            self._configure()
            
            self._make()
            
            self._make_install()
            
            if self.cfg.cleanup:
                self._cleanup()
            
            log.info("Done building")
            
            self.results['passed']=self.successfull_build
            
            os.chdir(self.cfg.build_dir)
            with open("results","at") as fout:
                fout.write(pprint.pformat(self.results,width=160)+",\n")
        except Exception as e:
            log.info("The build failed")
            traceback.print_exc()
            self.results['passed']=False
            self.results['message']=str(e)
        finally:
            os.chdir(old_wd)
        
        
        return self.results

