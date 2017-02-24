r.proj location=colimafine mapset=PERMANENT input=colima
r.fillnulls --overwrite --verbose input=colima@PERMANENT output=colima2 method=rst
r.compress -u -p --verbose map=colima@PERMANENT
r.compress -p --verbose map=colima@PERMANENT
r.compress -u -p --verbose map=colima@PERMANENT
r.compress -p --verbose map=colima@PERMANENT
r.compress -p map=colima@PERMANENT
export GRASS_COMPRESSOR=RLE
ls
ls colima 
export GRASS_INT_ZLIB=0
g.copy raster=colima,colimarle
r.compress colimarle
r.compress -p colimarle
r.compress -u colimarle
r.compress -p colimarle
r.compress colimarle
r.compress -p colimarle
r.compress -u colima
r.compress colima
