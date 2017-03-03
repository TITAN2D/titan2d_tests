"""Test Description:
Colima fine mini short serial run
"""
from TitestSingleTest import TitestSingleTest

class ThisTest(TitestSingleTest):
    def __init__(self,cfg,testname):
        super().__init__(cfg,testname)
        
        # normally should be done in about 13 seconds (debug, core i7-2600K)
        # so let timeout be 2 minutes
        self.timeout=2*60