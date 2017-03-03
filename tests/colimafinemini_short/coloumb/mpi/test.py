"""Test Description:
Colima fine mini short run using 4 MPI processes 
"""
from TitestSingleTest import TitestSingleTest

class ThisTest(TitestSingleTest):
    def __init__(self,cfg,testname):
        super().__init__(cfg,testname)
        self.mpi_procs=4
        self.input_dir='../serial/input'
        
        #tolerance for error in restart file
        self.err_tolerance={
            'h':5.0e-08 if not self.cfg.binary_identical else 0.0,
            'hVx':5.0e-08 if not self.cfg.binary_identical else 0.0,
            'hVy':5.0e-08 if not self.cfg.binary_identical else 0.0,
            'max_kinergy':5.0e-08 if not self.cfg.binary_identical else 0.0,
            'max_pileheight':5.0e-08 if not self.cfg.binary_identical else 0.0
        }
        
        #tolerance for error in visout (xdmf format) file
        self.err_visout_tolerance={
            'Pile_Height':5.0e-08,
            'XMomentum':5.0e-08,
            'YMomentum':5.0e-08
        }
        
        #tolerance for error in outline
        self.err_outline_tolerance={
            'maxkerecord':5.0e-08,
            'maxpileheightrecord':5.0e-08
        }
        
        # normally should be done in about 5 minutes (debug, core i7-2600K)
        # so let timeout be 10 minutes
        self.timeout=10*60
    