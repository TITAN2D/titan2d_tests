"""Test Description:
Colima fine mini short run using 4 threads 
"""
from TitestSingleTest import TitestSingleTest

class ThisTest(TitestSingleTest):
    def __init__(self,cfg,testname):
        super().__init__(cfg,testname)
        self.threads=4
    