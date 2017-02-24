import sys
import numpy

from collections import OrderedDict

def read_pilehight(filename):
    r={}
    with open(filename,"r") as fin:
        lines=fin.readlines()
    v=lines[0].replace("="," ").replace(","," ").replace(":"," ").replace("{"," ").replace("}"," ").split()
    r['Nx']=int(v[1])
    r['x0']=float(v[3])
    r['x1']=float(v[4])
    
    v=lines[1].replace("="," ").replace(","," ").replace(":"," ").replace("{"," ").replace("}"," ").split()
    r['Ny']=int(v[1])
    r['y0']=float(v[3])
    r['y1']=float(v[4])
    
    h=[]
    for line in lines[3:]:
        h+=[ float(x) for x in line.split() ]
    r['h']=numpy.asarray(h)
    return r

def compare_maxpilehights(filename,filename_ref):
    pilehight=read_pilehight(filename)
    pilehight_ref=read_pilehight(filename_ref)
    h=pilehight['h']
    h_ref=pilehight_ref['h']
    rmsd=numpy.sqrt(numpy.mean((h-h_ref)**2))
    hmax=numpy.max(h)
    hmin=numpy.min(h)
    hmean=numpy.mean(h)
    
    return OrderedDict([
        ("RMSD",rmsd),
        ("RelRMSD",rmsd/hmean if hmean!=0.0 else None),
        ("Mean",hmean),
        ("Max",hmax),
        ("Min",hmin),
    ])
    


if __name__ == '__main__':
    if(len(sys.argv)!=3):
        print("usage: compare_maxpilehights.py file1 file2")
    print(compare_maxpilehights(sys.argv[1],sys.argv[2]))
    
    