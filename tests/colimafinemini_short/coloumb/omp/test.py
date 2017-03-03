"""Test Description:
Colima fine mini short run using 4 threads 
"""
from TitestSingleTest import TitestSingleTest

class ThisTest(TitestSingleTest):
    def __init__(self,cfg,testname):
        super().__init__(cfg,testname)
        self.threads=4
        
        #input and reference is same as serial run
        self.input_dir='../serial/input'
        self.ref_dir="../serial/ref"
        
        # normally should be done in about 8 seconds (debug, core i7-2600K)
        # so let timeout be 2 minutes
        self.timeout=2*60
    
    