"""Test Description:
Colima fine mini short run using 4 MPI processes and 2 threads per each MPI process 
"""
from TitestSingleTest import TitestSingleTest

class ThisTest(TitestSingleTest):
    def __init__(self,cfg,testname):
        super().__init__(cfg,testname)
        self.threads=2
        self.mpi_procs=4
        self.input_dir='../serial/input'
        self.ref_dir="../mpi/ref"
        
        #tolerance for error in restart file
        self.err_tolerance={
            'h':2.0e-07 if not self.cfg.binary_identical else 0.0,
            'hVx':2.0e-07 if not self.cfg.binary_identical else 0.0,
            'hVy':2.0e-07 if not self.cfg.binary_identical else 0.0,
            'max_kinergy':2.0e-07 if not self.cfg.binary_identical else 0.0,
            'max_pileheight':2.0e-07 if not self.cfg.binary_identical else 0.0
        }
        
        #tolerance for error in visout (xdmf format) file
        self.err_visout_tolerance={
            'Pile_Height':2.0e-07,
            'XMomentum':2.0e-07,
            'YMomentum':2.0e-07
        }
        
        #tolerance for error in outline
        self.err_outline_tolerance={
            'maxkerecord':2.0e-07,
            'maxpileheightrecord':2.0e-07
        }
        # normally should be done in about 5 minutes (debug, core i7-2600K)
        # so let timeout be 10 minutes
        self.timeout=10*60
        