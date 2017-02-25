"""
Compares two hdf5 files generated for Paraview
"""

import sys
import h5py
import numpy
import math
from collections import OrderedDict

class TiRestartH5:
    def __init__(self,filename):
        self.filename=filename
        self.h5=h5py.File(self.filename, "r")
        
        if 'ElemTable' not in self.h5:
            raise Exception("There is no ElemTable group in %s. Is it Titan2d restart file?"%(self.filename,))
        #state vars 
        if 'state_vars_h' not in self.h5['ElemTable']:
            raise Exception("There is no state_vars_h dataset in ElemTable group in %s. Is it Titan2d restart file?"%(self.filename,))
        self.h=numpy.array(self.h5['ElemTable']['state_vars_h'])
        if 'state_vars_h' not in self.h5['ElemTable']:
            raise Exception("There is no state_vars_h dataset in ElemTable group in %s. Is it Titan2d restart file?"%(self.filename,))
        self.h=numpy.array(self.h5['ElemTable']['state_vars_h'])
        if 'state_vars_hVx' not in self.h5['ElemTable']:
            raise Exception("There is no state_vars_hVx dataset in ElemTable group in %s. Is it Titan2d restart file?"%(self.filename,))
        self.hVx=numpy.array(self.h5['ElemTable']['state_vars_hVx'])
        if 'state_vars_hVy' not in self.h5['ElemTable']:
            raise Exception("There is no state_vars_hVy dataset in ElemTable group in %s. Is it Titan2d restart file?"%(self.filename,))
        self.hVy=numpy.array(self.h5['ElemTable']['state_vars_hVy'])
        
        self.coord_X=numpy.array(self.h5['ElemTable']['coord_X'])
        self.coord_Y=numpy.array(self.h5['ElemTable']['coord_Y'])
        
        #outline
        if 'OutLine' not in self.h5:
            raise Exception("There is no OutLine group in %s. Is it Titan2d restart file?"%(self.filename,))
        if 'max_kinergy' not in self.h5['OutLine']:
            raise Exception("There is no max_kinergy dataset in OutLine group in %s. Is it Titan2d restart file?"%(self.filename,))
        self.max_kinergy=numpy.array(self.h5['OutLine']['max_kinergy'])
        if 'pileheight' not in self.h5['OutLine']:
            raise Exception("There is no pileheight dataset in OutLine group in %s. Is it Titan2d restart file?"%(self.filename,))
        self.max_pileheight=numpy.array(self.h5['OutLine']['pileheight'])

    def __del__(self):
        self.h5.close()

def compare_arrays(a1,a2):
    r=OrderedDict()
    r['Comparable']=a1.shape[0]==a2.shape[0]
    r['Err']=None
    r['ErrMax']=None
    if not r['Comparable']:
        return r
    r['Rel']=OrderedDict()
    r['Abs']=OrderedDict()
    r['Individual']=OrderedDict()
    N=a1.shape[0]
    N12_nonzero=numpy.count_nonzero(numpy.fabs(a1)+numpy.fabs(a2))
    
    sq_dev=(a1-a2)**2
    m_rmsd_nonzero=numpy.sum(sq_dev)/N12_nonzero
    m_rmsd=numpy.sum(sq_dev)/N
    m_mean1_nonzero=numpy.sum(a1)/numpy.count_nonzero(a1)
    m_mean1=numpy.sum(a1)/N
    m_mean2_nonzero=numpy.sum(a2)/numpy.count_nonzero(a2)
    m_mean2=numpy.sum(a2)/N
    m_mean_nonzero=(numpy.sum(a1)+numpy.sum(a2))/(numpy.count_nonzero(a1)+numpy.count_nonzero(a2))
    m_mean=(m_mean1+m_mean2)/2.0
    m_min1=a1.min()
    m_max1=a1.max()
    m_min2=a2.min()
    m_max2=a2.max()
    m_dmax=m_max1-m_max2
    m_dmean_nonzero=m_mean1_nonzero-m_mean2_nonzero
    m_dmean=m_mean1-m_mean2
    
    
    b_denom=numpy.ma.masked_equal((numpy.fabs(a1)+numpy.fabs(a2))*0.5,0.0)
    b_nom=numpy.ma.MaskedArray(numpy.fabs(a1-a2),mask=b_denom.mask)
    b=b_nom.compressed()/b_denom.compressed()
    r['Err']=b.mean()
    r['ErrMax']=b.max()
    r['Rel']['RMSD_NonZero']=m_rmsd_nonzero/m_mean_nonzero if m_mean_nonzero!=0.0 else None
    r['Rel']['RMSD']=m_rmsd/m_mean if m_mean!=0.0 else None
    r['Rel']['DiffMean_NonZero']=m_dmean_nonzero/m_mean_nonzero if m_mean_nonzero!=0.0 else None
    r['Rel']['DiffMean']=m_dmean/m_mean if m_mean!=0.0 else None
    r['Rel']['DiffMax_NonZero']=m_dmax/m_mean_nonzero if m_mean_nonzero!=0.0 else None
    r['Rel']['DiffMax']=m_dmax/m_mean if m_mean!=0.0 else None
    
    r['Abs']['RMSD_NonZero']=m_rmsd_nonzero
    r['Abs']['RMSD']=m_rmsd
    r['Abs']['DiffMean_NonZero']=m_dmean_nonzero
    r['Abs']['DiffMean']=m_dmean
    r['Abs']['DiffMax']=m_dmax

    r['Individual']['Min1']=m_min1
    r['Individual']['Min2']=m_min2
    r['Individual']['Mean1']=m_mean2
    r['Individual']['Mean2']=m_mean2
    r['Individual']['Mean1_NonZero']=m_mean1_nonzero
    r['Individual']['Mean2_NonZero']=m_mean2_nonzero
    r['Individual']['Max1']=m_max1
    r['Individual']['Max2']=m_max2
    r['Individual']['CountNonZero1']=numpy.count_nonzero(a1)
    r['Individual']['CountNonZero2']=numpy.count_nonzero(a2)
        
    return r

def compare_restart_hdf5(filename1,filename2,verbose=False):
    """compare restarts files"""
    #print "Comparing "+filename1+" and "+filename2
    
    f1 = TiRestartH5(filename1)
    f2 = TiRestartH5(filename2)
    
    r=OrderedDict()
    
    r['same_elements']=True
    
    if not numpy.array_equal(f1.coord_X,f2.coord_X):
        r['same_elements']=False
    if not numpy.array_equal(f1.coord_Y,f2.coord_Y):
        r['same_elements']=False
    
    if r['same_elements']:
        r['h']= compare_arrays(f1.h,f2.h)
        r['hVx']= compare_arrays(f1.hVx,f2.hVx)
        r['hVy']= compare_arrays(f1.hVy,f2.hVy)
    
    r['max_kinergy']=compare_arrays(f1.max_kinergy,f2.max_kinergy)
    r['max_pileheight']=compare_arrays(f1.max_pileheight,f2.max_pileheight)
    
    return r

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print("Usage:")
        print("\tpython compare_restart_hdf5.py file1 file2")

    r=compare_restart_hdf5(sys.argv[1],sys.argv[2],verbose=True)
    import pprint
    print(pprint.pformat(r))


