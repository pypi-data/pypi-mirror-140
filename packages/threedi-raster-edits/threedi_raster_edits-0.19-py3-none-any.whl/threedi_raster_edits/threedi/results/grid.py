# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 13:52:55 2019

@author: chris.kerklaan

# one can import threedigrid easily from here
# module only loads if threedigrid is present
"""
import numpy as np
from threedi_raster_edits import Vector, Point
from threedi_raster_edits.utils.project import _check_installed


HAS_THREEDIGRID = _check_installed("threedigrid") and _check_installed("h5py")


if HAS_THREEDIGRID:
    from threedigrid.admin.gridresultadmin import GridH5ResultAdmin
    from threedigrid.admin.gridadmin import GridH5Admin

    class Grid:
        def __init__(self, results_folder):
            self.h5_file_path = results_folder + "/gridadmin.h5"
            self.netcdf_file_path = results_folder + "/results_3di.nc"
            self.gr = GridH5ResultAdmin(self.h5_file_path, self.netcdf_file_path)
            self.ga = GridH5Admin(self.h5_file_path)

            self.start_time = 0
            self.end_time = self.gr.nodes.timestamps[-1]

        @property
        def nodes(self):
            if not hasattr(self, "_nodes"):
                self.set_nodes()

            return self._nodes

        def set_nodes(self):
            self._nodes = Vector.from_scratch("nodes", 1, 28992)
            coordinates = np.vstack(self.gr.nodes.coordinates.T)
            ids = self.gr.nodes.id
            for id, coordinate in zip(ids, coordinates):
                self._nodes.add(geometry=Point.from_point(coordinate), fid=id)

        def level(self, grid_id=[], model_id=[], start_time=0, end_time=None):
            """retrieves the waterlevel for different either model ids or grid ids
            params:
                grid_id: grid id, list or integer
                model_id: model id, list or integer
                start_time: start time, as a datetime object
                end_time: end time, as a datetime object
            """

            if not end_time:
                self.end_time = end_time

            if type(grid_id) == int:
                return list(
                    self.gr.nodes.filter(id=grid_id)
                    .timeseries(start_time, self.end_time)
                    .s1.flatten()
                )

            if type(model_id) == int:
                return list(self.gr.nodes.filter(content_pk=model_id).s1.flatten())

            output_dict = {}
            if len(grid_id) > 0:
                for gid in grid_id:
                    output_dict[gid] = list(self.gr.nodes.filter(id=gid).s1.flatten())

            if len(model_id) > 0:
                for mid in model_id:
                    output_dict[mid] = list(
                        self.gr.nodes.filter(content_pk=mid).s1.flatten()
                    )

            return output_dict

        def discharge(
            self, grid_id=[], model_id=[], model_type=None, start_time=0, end_time=None
        ):
            """retrieves the dicharge for different either model ids or grid ids
            params:
                grid_id: grid id, list or integer
                model_id: model id, list or integer
                start_time: start time, as a datetime object
                end_time: end time, as a datetime object
                type: 'v2_weir','v2_orifice' etc.
            """

            if not end_time:
                self.end_time = end_time

            if type(grid_id) == int:
                return list(
                    self.gr.lines.filter(id=grid_id)
                    .timeseries(start_time, self.end_time)
                    .q.flatten()
                )

            if type(model_id) == int:
                return list(
                    self.gr.lines.filter(content_pk=model_id, content_type=model_type)
                    .timeseries(start_time, end_time)
                    .q.flatten()
                )

            output_dict = {}
            if len(grid_id) > 0:
                for gid in grid_id:
                    output_dict[gid] = list(self.gr.lines.filter(id=gid).q.flatten())

            if len(model_id) > 0:
                for mid in model_id:
                    output_dict[mid] = list(
                        self.gr.lines.filter(content_pk=mid).q.flatten()
                    )

            return output_dict
