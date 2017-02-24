sim=TitanSimulation(overwrite_output=True)

sim.setGIS(
    gis_format='GIS_GRASS',
    gis_main='LOCATION_OF_TITAN2D_TESTS/dem',
    gis_sub='colimafinemini',
    gis_mapset='PERMANENT',
    gis_map='colimarle'
)

sim.setScale(
    length_scale=4000.0,
    gravity_scale=9.8
)

sim.setNumProp(
    AMR=True,
    number_of_cells_across_axis=16,
    order='First',
    short_speed=False,
    geoflow_tiny=0.0001
)
sim.setMatModel(
    model='Coulomb',
    int_frict=37.0,
    bed_frict=27.0
)
sim.addPile(
    height=30.0,
    center=[644956.0, 2157970.0],
    radii=[55.0, 55.0],
    orientation=0.0,
    Vmagnitude=0.0,
    Vdirection=0.0
)
sim.setTimeProps(
    max_iter=300
)

sim.setTimeSeriesOutput(
    vizoutput='xdmf',
    dtime=1.0,
    diter=None
)
sim.setRestartOutput(
    dtime=None,
    diter=None
)
sim.setStatProps()
sim.run()
