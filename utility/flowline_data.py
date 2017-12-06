import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import fenics as fc


"""
Calculates surface, smb, thickness, etc. on a given a flowline graph.
"""

class FlowlineData():

    def __init__(self, main_window, fg):
        # Flowline graph
        self.main_window = main_window
        # Flowline graph
        self.fg = fg

        # Flowline center points
        self.center_coords = fg.getCenterCoords()
        self.center_xs = self.center_coords[:,0]
        self.center_ys = self.center_coords[:,1]

        # Compute along flowline distance
        self.distances = np.sqrt(((self.center_coords[1:] - self.center_coords[:-1])**2).sum(axis = 1))
        self.distances = np.insert(self.distances, 0, 0.)
        # Distance multiplier to convert from view coordinates to a real distance in meters
        dist_mult = 150.
        self.distances = np.cumsum(self.distances) * dist_mult
        # Flip so divide is at 0
        #self.distances = self.distances[::-1]
        #self.distances = self.distances[0] - self.distances


        ### Get flowline data
        self.flowline_data = {}

        # Bed
        self.flowline_data['bed'] = main_window.data_loader.interp_fields['bed'](self.center_xs, self.center_ys, grid = False)
        # Surface
        self.flowline_data['surface'] = main_window.data_loader.interp_fields['surface'](self.center_xs, self.center_ys, grid = False)
        # smb
        self.flowline_data['smb'] = main_window.data_loader.interp_fields['smb'](self.center_xs, self.center_ys, grid = False)
        # Convert milimeters of water equivalent to meters of ice equivalent
        self.flowline_data['smb'] *= (1.0/1000.0)*(916.7/1000.0)
        # Ice stream width
        self.flowline_data['width'] = fg.getWidth() * dist_mult
        # Velocity magnitude
        self.flowline_data['velocity'] = main_window.data_loader.interp_fields['velocity'](self.center_xs, self.center_ys, grid = False)



    ### Generate a mesh and write flowline data for fenics
    def write_data(self, file_name):

        print file_name


        ### Create a 1d mesh

        editor = fc.MeshEditor()
        mesh = fc.Mesh()
        editor.open(mesh, 1, 1)

        editor.init_vertices(len(self.center_xs))
        editor.init_cells(len(self.center_xs) - 1)

        # Add vertices
        i = 0
        for d in self.distances:
            editor.add_vertex(i, d)
            i += 1

        # Add cells
        for i in range(len(self.distances) - 1):
            editor.add_cell(i, np.array([i, i+1], dtype = np.uintp))

        editor.close()


        ### Create output hdf5 file

        out_file = fc.HDF5File(mesh.mpi_comm(), file_name, "w")


        ### Create and set data functions

        V = fc.FunctionSpace(mesh, "CG", 1)
        smb = fc.Function(V)
        surface = fc.Function(V)
        bed = fc.Function(V)
        width = fc.Function(V)
        thickness = fc.Function(V)

        smb.vector().set_local(self.flowline_data['smb'])
        smb.vector().apply("insert")
        surface.vector().set_local(self.flowline_data['surface'])
        surface.vector().apply("insert")
        bed.vector().set_local(self.flowline_data['bed'])
        bed.vector().apply("insert")
        width.vector().set_local(self.flowline_data['width'])
        width.vector().apply("insert")
        thickness.vector().set_local(self.flowline_data['surface'] - self.flowline_data['bed'])
        thickness.vector().apply("insert")


        out_file.write(mesh, "/mesh")
        out_file.write(smb.vector(), "/smb")
        out_file.write(surface.vector(), "/surface")
        out_file.write(bed.vector(), "/bed")
        out_file.write(width.vector(), "/width")
        out_file.write(thickness.vector(), "/thickness")
        out_file.close()
