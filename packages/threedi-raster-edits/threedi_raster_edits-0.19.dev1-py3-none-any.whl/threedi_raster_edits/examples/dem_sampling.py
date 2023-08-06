# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 10:39:47 2021

@author: chris.kerklaan

Steps for sampling/reading data from vector geometries and burning it back to 
the dem. 
"""
import os
import numpy as np
from threedi_raster_edits import Vector, Raster, Progress

dem_path = r"data/09bn2.tif"
buildings_path = r"data/Panden_nieuw.shp"
tegel_path = r"data/AHN_HHNK_grenzen.shp"

os.chdir(r"C:\Users\chris.kerklaan\Documents\Projecten\basis kaarten hhnk\processing")

# load raster
dem = Raster(dem_path)

# get dem tile
tegels = Vector(tegel_path)
tegel = tegels.filter(name='09bn2')[0]

# get buildings within tile.
buildings = Vector(buildings_path, create_index=True)
buildings_within_tile = buildings.spatial_filter(tegel.geometry)

# make output
output = buildings.copy(shell=True)
output.add_field("level", float)

# find percentile, add buffer
for building in buildings_within_tile:
    
    # do a 1 meter buffer
    geometry_buffered = building.geometry.buffer(1)
    
    # difference with the original to create a hull
    difference = geometry_buffered.difference(building.geometry)
    
    # read the data
    data = dem.read(difference)
    
    # find the percentile
    percentile = np.percentile(data, 75)
    
    # percentile + 5 cm
    floorheight = percentile + 0.05
    
    # write to output with new fields
    items = building.items
    items['level'] = floorheight
    output.add(items=items, geometry=building.geometry)

output.write("building_output.shp")

# find out how to find functions
dir(dem) 

# find arguments 
help(dem.push_vector)

# push the data onto the raster
dem_floorheight = dem.push_vector(output, field="level")
dem_floorheight.write("dem_level.tif")


# Use the above data as a function a loop over multiple tiles
def burn_floorlevels_in_tile(dem_tile:Raster, buildings:Vector, output_raster_path):    
    # get buildings within tile. Slightly different then the above method
    # we are now directory getting the extent from the raster with raster.extent_geometry
    buildings_within_tile = buildings.spatial_filter(dem_tile.extent_geometry)
    
    # make output
    output = buildings.copy(shell=True)
    output.add_field("level", float)
    
    # find percentile, add buffer
    for building in buildings_within_tile:
        
        # do a 1 meter buffer
        geometry_buffered = building.geometry.buffer(1)
        
        # difference with the original to create a hull
        difference = geometry_buffered.difference(building.geometry)
        
        # read the data
        data = dem_tile.read(difference)
        
        # find the percentile
        percentile = np.percentile(data, 75)
        
        # percentile + 5 cm
        floorheight = percentile + 0.05
        
        # write to output with new fields
        items = building.items
        items['level'] = floorheight
        output.add(items=items, geometry=building.geometry)

    dem_floorheight = dem.push_vector(output, field="level")
    dem_floorheight.write(output_raster_path)


# Now we are using this function to automate our processes
dem_directory = r"\\utr-3fs-01.nens.local\WorkDir\J_vLieshout\HHNK_AHN_basiskaarten\1_AHN4_Interpolated\ahn4"

# We can only show our progress using the Progress class as is show below
for dem_file in Progress(dem_directory, "Generating floorlevels"):
    
    # skip the file if it does not end with '.tif'
    if not dem_file.endswith(."tif"):
        continue
    
    # load data
    dem_tile = Raster(dem_directory + "/" + dem_file)
    buildings = Vector(r"\\utr-3fs-01.nens.local\WorkDir\J_vLieshout\HHNK_AHN_basiskaarten\Panden\panden_met_index.shp")
    
    # make output path
    output_raster_path = r"\\utr-3fs-01.nens.local\WorkDir\J_vLieshout\HHNK_AHN_basiskaarten\1_AHN4_Interpolated\ahn4_vloerpijl/" + dem_file
    
    # start processing
    burn_floorlevels_in_tile(dem_tile, buildings, output_raster_path)
    


    