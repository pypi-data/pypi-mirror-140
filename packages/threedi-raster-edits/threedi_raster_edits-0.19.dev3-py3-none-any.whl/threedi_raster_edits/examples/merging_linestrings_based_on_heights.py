# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 09:15:34 2021

@author: chris.kerklaan

"""

# imports
import os
import sys
import numpy as np

sys.path.append(r"C:\Users\chris.kerklaan\Documents\Github\threedi-raster-edits")
from threedi_raster_edits import Vector, Raster, Progress, LineString, RasterGroup


def split(levees, distance=5):
    # first cut into pieces of 5 meter and sample some dem values
    split = levees.copy(shell=True)
    for levee in Progress(levees, "Splitting"):
        # create single levees due to multilinestrings
        for single_levee in levee.geometry.to_single():
            # split the levee in sections of 5 meter
            levee_lines = LineString(single_levee).split(distance)
            for levee_line in levee_lines:
                split.add(geometry=levee_line, items=levee.items)
    return split


def sample(levees, dem, distance=2, perpendicular_length=10):
    sampled = levees.copy(shell=True)
    sampled.add_field("height", float)
    for levee in Progress(levees, "Sampling"):
        lines = levee.geometry.perpendicular_lines(distance, perpendicular_length)
        heights = []
        for line in lines:
            line_data = dem.read(line)
            try:
                if len(line_data) > 0:
                    heights.append(np.nanmax(line_data))
            except Exception as e:
                print(e)
                pass
        mean = float(np.nanmean(heights))
        sampled.add(items=levee.items, height=mean, geometry=levee.geometry)

    return sampled


class Merge:
    def __init__(self, levees, field=None, height_field="height"):

        if field:
            field_data = {}
            for value in list(set(levees.table[field])):
                field_data[value] = levees.filter(return_vector=True, **{field: value})
            self.field_data = field_data
        self.data = levees.copy()

    def add_fields(self, output):
        output.add_field("m_count", int)
        output.add_field("m_aheight", float)
        output.add_field("m_max", float)
        output.add_field("m_min", float)
        return output

    def run_fields(self, threshold=0.25, thresholds={}):
        field_output = self.data.copy(shell=True)
        field_output = self.add_fields(field_output)
        for field, data in self.field_data.items():
            if thresholds:
                threshold = thresholds[field]

            print("Running:", field, "Threshold:", threshold)
            output = self.run(data, threshold)
            for feature in output:
                field_output.add(feature)
        return field_output

    def run(self, data, threshold=0.25):
        output = data.copy(shell=True)
        output = self.add_fields(output)

        data = data.copy()
        data.reset()
        levee = next(data)
        levee_geometry = levee.geometry
        levee_items = levee.items
        heights = [levee["height"]]
        data.delete(levee)

        while len(data) != 0:
            data.reset()
            levee_geometry, added_levees = add_adjacent_levees(
                heights, levee_geometry, data, threshold
            )

            if len(added_levees) == 0:
                # add to ouput
                output.add(
                    geometry=levee_geometry,
                    items=levee_items,
                    m_count=len(heights),
                    m_height=np.nanmean(heights),
                    m_max=np.nanmax(heights),
                    m_min=np.nanmin(heights),
                )

                levee = next(data)  # retrieves a new feature even if some are deleted
                levee_items = levee.items
                levee_geometry = levee.geometry
                heights = [levee["height"]]
                data.delete(levee)

            else:
                # delete from data and to heights
                for levee_id in added_levees:
                    added_levee = data[levee_id]
                    heights.append(added_levee["height"])
                    data.delete(added_levee)

        data.close()

        return output


def add_adjacent_levees(heights, levee_geometry, levee_vector, threshold=0.25):
    output_geometry = levee_geometry.copy()
    added_levees = []
    for levee in levee_vector.spatial_filter(levee_geometry.buffer(0.0001)):
        next_levee_height = levee["height"]
        minimum_difference = abs(next_levee_height - min(heights)) < threshold
        maximum_difference = abs(next_levee_height - max(heights)) < threshold
        is_nan = np.isnan(next_levee_height)
        if (minimum_difference and maximum_difference) or is_nan:
            added_levees.append(levee.id)
            output_geometry = output_geometry.union(levee.geometry)
            output_geometry = output_geometry.dissolve()

    return output_geometry, added_levees


if __name__ == "__main__":

    os.chdir(
        r"C:\Users\chris.kerklaan\Documents\Projecten\basis kaarten hhnk\processing"
    )
    # define linestring paths
    # levee_path = r"levees/merged.gpkg"
    # dem_path = r"data/19gz2.tif"
    # dem = Raster(dem_path)
    # levees = Vector(levee_path)

    # threshold = 0.25
    # levees = Vector("levees/all_levees.gpkg")
    # splitted = split(levees, distance=10)
    # splitted.write("levees/split_10m.gpkg")

    ## sampling
    # levees = Vector("levees/split_10m.gpkg")

    # dem_tiles_dir = r"\\utr-3fs-01.nens.local\WorkDir\J_vLieshout\HHNK_AHN_basiskaarten\AHN4_DTM"
    # dem_tiles = [
    #     Raster(dem_tiles_dir + f"/{i}")
    #     for i in os.listdir(dem_tiles_dir)
    #     if i.endswith("tif")
    # ]
    # dem = RasterGroup(dem_tiles)
    # sampled = sample(levees, dem, distance=2, perpendicular_length=10)
    # sampled.write("levees/sampled_10m.gpkg")

    # ## merging
    thresholds = {
        "kering-primair": 0.25,
        "kering-secundair": 0.1,
        "weg": 0.5,
        "spoor": 0.5,
    }
    samples = Vector("levees/sampled_10m.gpkg")
    merge = Merge(samples, field="type", height_field="height")
    output = merge.run_fields(thresholds=thresholds)

    output.write("levees/merged.gpkg")
