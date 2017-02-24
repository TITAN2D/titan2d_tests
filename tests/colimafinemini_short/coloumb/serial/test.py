"""Test Description:
Colima fine mini short serial run
"""
from TitestSingleTest import TitestSingleTest

class ThisTest(TitestSingleTest):
    def __init__(self,cfg,testname):
        super().__init__(cfg,testname)
        #input and reference is same as omp run
        self.input_dir='../omp/input'
        self.ref_dir="../omp/ref"
    