import os
import logging as log
from collections import OrderedDict
from TitestCommon import run_command

class TitestSrc:
    """base class for obtain code sources grabers"""
    def __init__(self,cfg):
        self.cfg=cfg
        
    def get_src(self):
        """obtain code sources"""
        pass
    
    def run_autotools(self):
        old_wd=os.getcwd()
        os.chdir(self.cfg.titan2d_src_dir)
        
        log.info("Running autotools")
        if self.cfg.redo_src==False:
            if os.path.exists(os.path.join(self.cfg.titan2d_src_dir,'configure')):
                if os.path.exists(os.path.join(self.cfg.titan2d_src_dir,'Makefile.in')):
                    log.info("\tautotools were ran previously, would not run them now")
                    os.chdir(old_wd)
                    return
        
        run_command('aclocal', True)
        run_command('autoheader', True)
        run_command('autoconf', True)
        run_command('automake --add-missing --copy', True)
        
        if not os.path.exists(os.path.join(self.cfg.titan2d_src_dir,'configure')):
            raise Exception("Can not find configure. Autotools didnt run well!")
        if not os.path.exists(os.path.join(self.cfg.titan2d_src_dir,'Makefile.in')):
            raise Exception("Can not find Makefile.in. Autotools didnt run well!")
        
        os.chdir(old_wd)

    
class TitestGit(TitestSrc):
    """obtain titan2d code from github repo"""
    def __init__(self,cfg):
        super().__init__(cfg)
        self.remote_git_repo='https://github.com/TITAN2D/titan2d'
        
    def check_local_git_repo(self, redo_git=False):
        """check presence of local git repo if it is not present clone it from git hub"""
        if os.path.exists(self.cfg.titan2d_src_dir) and not os.path.isdir(self.cfg.titan2d_src_dir):
            raise Exception("Local git repo (%s) exists but is not directory"%(self.cfg.titan2d_src_dir,))
        if os.path.exists(os.path.join(self.cfg.titan2d_src_dir,'.git')) and self.cfg.redo_src==False:
            log.info("\tgit repo already there don't need to clone")
            return
            
        if self.cfg.redo_src and os.path.isdir(self.cfg.titan2d_src_dir):
            if os.path.dirname(self.cfg.titan2d_src_dir)==self.cfg.test_space_dir:
                log.info("Local git repo exist, but asked to redo it")
                run_command('rm -rf '+self.cfg.titan2d_src_dir)
            else:
                raise Exception("titan2d_src_dir (%s) is not in test_space_dir (%s). Can not redo it."%(self.cfg.titan2d_src_dir,self.cfg.test_space_dir))
            
        
        if not os.path.isdir(self.cfg.titan2d_src_dir):
            old_wd=os.getcwd()
            os.chdir(os.path.dirname(self.cfg.titan2d_src_dir))
            log.info("Local git repo doesn't exist. Clonning to "+self.cfg.titan2d_src_dir)
            run_command('git clone '+self.remote_git_repo+' '+self.cfg.titan2d_src_dir, True)
            os.chdir(old_wd)
        else:
            log.debug("Local git repo (%s) exist."%(self.cfg.titan2d_src_dir,))
        
        if not (os.access(self.cfg.titan2d_src_dir, os.W_OK) and os.access(self.cfg.titan2d_src_dir, os.R_OK)):
            raise Exception("Can not read or write to local git repo: "+self.cfg.titan2d_src_dir)
        
        if not os.path.exists(os.path.join(self.cfg.titan2d_src_dir,'configure.ac')):
            raise Exception("Can not find configure.ac. Getting code didnt went well!")
    
    def checkout(self, branch,pull=False):
        old_wd=os.getcwd()
        log.info("Checking out "+branch)
        os.chdir(self.cfg.titan2d_src_dir)
        run_command('git checkout '+branch, True)
        if pull:
            log.info("pulling latest changes")
            run_command('git pull', True)
        os.chdir(old_wd)
        
    def get_src(self):
        old_wd=os.getcwd()
        
        self.check_local_git_repo(redo_git=False)
        self.checkout(self.cfg.commit,pull=False)
        
        self.run_autotools()
        
        os.chdir(old_wd)
        
        return OrderedDict([
            ('passed',True),
            ('message',"")
        ])