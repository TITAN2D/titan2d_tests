"""
Compares two hdf5 files generated for Paraview
"""

import sys
import h5py
import numpy
import math
from collections import OrderedDict

def compare_vizout_hdf5(filename1,filename2,verbose=False):
    
    #print "Comparing "+filename1+" and "+filename2
    
    f1 = h5py.File(filename1, "r")
    f2 = h5py.File(filename2, "r")
    
    propnamedict={
        'PILE_HEIGHT':'Pile_Height', 
        'XMOMENTUM':'XMomentum', 
        'YMOMENTUM':'YMomentum'
    }
    
    r=OrderedDict()
    #check number of elements
    ds1=numpy.array(f1['Properties']['PILE_HEIGHT'])
    ds2=numpy.array(f2['Properties']['PILE_HEIGHT'])
    if ds1.shape!=ds2.shape:
        r['ElementsNumberIsSame']=False
        r['XCoordRMSD']=None
        r['YCoordRMSD']=None
        for prop in ('PILE_HEIGHT', 'XMOMENTUM', 'YMOMENTUM'):
            r[prop+'_RMSD']=None
            r[prop+'_Mean']=None
        return r
    else:
        r['ElementsNumberIsSame']=True
    #compare Mash
    #print "Comparing Mesh/Points"
    ds1=numpy.array(f1['Mesh']['Points'])
    ds2=numpy.array(f2['Mesh']['Points'])
    if ds1.shape!=ds2.shape:
        #print "\tDatasets have different size!"
        r['PointsNumberIsSame']=False
        r['PointsRMSD']=None
    else:
        ds=(ds1-ds2)*(ds1-ds2)
        rmsd=math.sqrt(ds.mean())
        r['PointsNumberIsSame']=True
        r['PointsRMSD']=rmsd
        #print "\tRMSD=%.3e Mean1=%.3e RMSD/Mean1=%.3e"%(rmsd,ds1.mean(),rmsd/ds1.mean())
    if r['PointsNumberIsSame']==False or (r['PointsNumberIsSame']==True and r['PointsRMSD']>0.0):
        r['PointsRMSD']=None
        heights_dss=[]
        for f in [f1,f2]:
            conn=numpy.array(f['Mesh']['Connections'])
            coor=numpy.array(f['Mesh']['Points'])
            nelem=conn.shape[0]
            heights_ds=numpy.zeros((nelem,), dtype=[
                ('x', numpy.float64), ('y', numpy.float64),
                ('PILE_HEIGHT', numpy.float64), ('XMOMENTUM', numpy.float64), ('YMOMENTUM', numpy.float64)])
            
            h=numpy.array(f1['Properties']['PILE_HEIGHT'])
            xmom=numpy.array(f['Properties']['XMOMENTUM'])
            ymom=numpy.array(f['Properties']['YMOMENTUM'])
            
            for i in range(conn.shape[0]):
                heights_ds['x'][i]=min(coor[conn[i,0],0],coor[conn[i,1],0],coor[conn[i,2],0],coor[conn[i,3],0])
                heights_ds['y'][i]=min(coor[conn[i,0],1],coor[conn[i,1],1],coor[conn[i,2],1],coor[conn[i,3],1])
                heights_ds['PILE_HEIGHT'][i]=h[i,0]
                heights_ds['XMOMENTUM'][i]=xmom[i,0]
                heights_ds['YMOMENTUM'][i]=ymom[i,0]
            heights_ds=numpy.sort(heights_ds,order=['x','y'])
            heights_dss.append(heights_ds)
        r['XCoordRMSD']=numpy.sqrt(numpy.mean((heights_dss[0]['x']-heights_dss[1]['x'])**2))
        r['YCoordRMSD']=numpy.sqrt(numpy.mean((heights_dss[0]['y']-heights_dss[1]['y'])**2))
        
        for prop in ('PILE_HEIGHT', 'XMOMENTUM', 'YMOMENTUM'):
            propname=propnamedict[prop]
            
            ds1=heights_dss[0][prop]
            ds2=heights_dss[1][prop]
            sq_dev=(ds1-ds2)**2
            m_rmsd=numpy.sum(sq_dev)/numpy.count_nonzero(sq_dev)
            m_mean1=numpy.sum(ds1)/numpy.count_nonzero(ds1)
            m_mean2=numpy.sum(ds2)/numpy.count_nonzero(ds2)
            m_mean=(numpy.sum(ds1)+numpy.sum(ds2))/(numpy.count_nonzero(ds1)+numpy.count_nonzero(ds2))
            m_min1=ds1.min()
            m_max1=ds1.max()
            m_min2=ds2.min()
            m_max2=ds2.max()
            m_dmax=m_max1-m_max2
            m_dmean=m_mean1-m_mean2
            
            r[propname+'_relRMSD_NonZero']=m_rmsd/m_mean if m_mean!=0.0 else None
            r[propname+'_relMeanDiff_NonZero']=m_dmean/m_mean if m_mean!=0.0 else None
            r[propname+'_relMaxDiff']=m_dmax/m_mean if m_mean!=0.0 else None
            r[propname+'_RMSD_NonZero']=rmsd
            r[propname+'_MeanDiff_NonZero']=m_dmean
            r[propname+'_MaxDiff']=m_dmax
            r[propname+'_Mean1']=m_mean1
            r[propname+'_Min1']=m_min1
            r[propname+'_Max1']=m_max1
        f2.close()
        f1.close()
        return r
    else:
        #compare Mash
        #print "Comparing Mesh/Connections"
        ds1=numpy.array(f1['Mesh']['Connections'])
        ds2=numpy.array(f2['Mesh']['Connections'])
        if ds1.shape!=ds2.shape:
            #print "\tDatasets have different size!"
            r['ConnectionsIsSame']=False
        else:
            ds=ds1-ds2
            msum=ds.sum()
            if msum>0:
                r['ConnectionsIsSame']=False
                #print "\tConnections are different!"
            else:
                r['ConnectionsIsSame']=True
                #print "\tConnections are identical"
        
        #compare Properties
        for prop in ('PILE_HEIGHT', 'XMOMENTUM', 'YMOMENTUM'):
            propname=propnamedict[prop]
            #print "Comparing Properties/"+prop
            
            ds1=numpy.array(f1['Properties'][prop])
            ds2=numpy.array(f2['Properties'][prop])
            if ds1.shape!=ds2.shape:
                #print "\tDatasets have different size!"
                r[prop+'_RMSD']=None
                r[prop+'_relRMSD']=None
                r[prop+'_Mean']=None
                continue
            
            sq_dev=(ds1-ds2)**2
            m_rmsd=numpy.sum(sq_dev)/numpy.count_nonzero(ds1+ds2)
            m_mean1=numpy.sum(ds1)/numpy.count_nonzero(ds1)
            m_mean2=numpy.sum(ds2)/numpy.count_nonzero(ds2)
            m_mean=(numpy.sum(ds1)+numpy.sum(ds2))/(numpy.count_nonzero(ds1)+numpy.count_nonzero(ds2))
            m_min1=ds1.min()
            m_max1=ds1.max()
            m_min2=ds2.min()
            m_max2=ds2.max()
            m_dmax=m_max1-m_max2
            m_dmean=m_mean1-m_mean2
            
            r[propname+'_relRMSD_NonZero']=m_rmsd/m_mean if m_mean!=0.0 else None
            r[propname+'_relMeanDiff_NonZero']=m_dmean/m_mean if m_mean!=0.0 else None
            r[propname+'_relMaxDiff']=m_dmax/m_mean if m_mean!=0.0 else None
            r[propname+'_RMSD_NonZero']=m_rmsd
            r[propname+'_MeanDiff_NonZero']=m_dmean
            r[propname+'_MaxDiff']=m_dmax
            r[propname+'_Mean1']=m_mean1
            r[propname+'_Min1']=m_min1
            r[propname+'_Max1']=m_max1
            #print "\tRMSD=%.3e Mean1=%.3e RMSD/Mean1=%.3e"%(rmsd,ds1.mean(),rmsd/ds1.mean())
        f2.close()
        f1.close()
        
        return r


if __name__ == '__main__':
    if len(sys.argv)!=3:
        print("Usage:")
        print("\tpython compare_hdf5.py file1 file2")

    r=compare_vizout_hdf5(sys.argv[1],sys.argv[2],verbose=True)
    import pprint
    print(pprint.pformat(r))


