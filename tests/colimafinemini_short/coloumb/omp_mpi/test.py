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
        self.ref_dir="../serial/ref"
        
        # normally should be done in about 5 minutes (debug, core i7-2600K)
        # so let timeout be 10 minutes
        self.timeout=10*60
        