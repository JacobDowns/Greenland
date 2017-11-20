
from PyQt4 import QtCore, QtGui
import h5py
import numpy as np
from scipy.interpolate import RectBivariateSpline


""" Object for loading and accessing data. """

class DataWrapper():

    def __init__(self):

        # File with data
        self.data_file_name = './data/greenland_data.h5'
        self.data_file = h5py.File(self.data_file_name, 'r')
        # File with color maps
        self.color_file_name = './data/color_data.h5'
        self.color_file = h5py.File(self.color_file_name, 'r')


        ### Load data arrays
        #######################################################################

        print "Loading data..."
        print

        # x component of velocity
        self.vx_array = self.data_file['VX'][:]
        # x component of velocity
        self.vy_array = self.data_file['VX'][:]
        # velocity magnitude
        self.v_mag = np.sqrt(self.vx_array**2 + self.vy_array**2)
        # Bed elevation
        self.bed_array = self.data_file['bed'][:]
        # Surface elevation
        self.surface_array = self.data_file['surface'][:]
        # Surface mass balance
        self.smb_array = self.data_file['smb'][:]
        # Ice thickness
        self.thickness_array = self.data_file['thickness'][:]

        print "Done."
        print


        ### Load color data for each field
        #######################################################################

        print "Loading colors..."
        print

        self.velocity_color = self.color_file['smb'][:]
        self.bed_color = self.color_file['bed'][:]
        self.surface_color = self.color_file['surface'][:]
        self.thickness = self.color_file['thickness'][:]
        self.velocity = self.color_file['velocity'][:]

        print "Done."
        print


        ### Load color map data for each field
        #######################################################################

        print "Loading color maps..."
        print

        self.smb_cmap_p = self.color_file['smb_cmap_p'][:]
        self.smb_cmap_c = self.color_file['smb_cmap_c'][:]
        self.bed_cmap_p = self.color_file['bed_cmap_p'][:]
        self.bed_cmap_p = self.color_file['bed_cmap_p'][:]
        self.surface_cmap_p = self.color_file['surface_cmap_p'][:]
        self.surface_cmap_c = self.color_file['surface_cmap_c'][:]
        self.thickness_cmap_p = self.color_file['thickness_cmap_p'][:]
        self.thickness_cmap_c = self.color_file['thickness_cmap_c'][:]
        self.velocity_cmap_p = self.color_file['velocity_cmap_p'][:]
        self.velocity_cmap_c = self.color_file['velocity_cmap_c'][:]

        print "Done."
        print


        ### Create interpolated data fields
        #######################################################################

        print "Interpolating..."
        print

        # Grid coordinates
        x_min = 0.0
        x_max = self.bed_array.shape[1]
        y_min = 0.0
        y_max = self.bed_array.shape[0]

        # x and y grid coordinates
        self.x_array = np.linspace(x_min, x_max, x_max, endpoint = True)
        self.y_array = np.linspace(y_min, y_max, y_max, endpoint = True)

        self.vx_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.vx_array).transpose())
        self.vy_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.vy_array).transpose())
        self.v_mag_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.v_mag).transpose())
        self.bed_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.bed_array).transpose())
        self.surface_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.surface_array).transpose())
        self.smb_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.smb_array).transpose())
        self.thickness_interp = RectBivariateSpline(self.x_array, self.y_array, np.flipud(self.thickness_array).transpose())

        print "Done."
        print


dw = DataWrapper()
