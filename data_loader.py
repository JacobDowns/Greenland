
from PyQt4 import QtCore, QtGui
import h5py
import numpy as np
from scipy.interpolate import RectBivariateSpline


""" Object for loading and interpolating raw data. """

class DataLoader():

    def __init__(self):

        # Data fields
        fields = ['smb', 'bed', 'surface', 'thickness', 'VX', 'VY']

        # File with data
        self.data_file_name = './data/greenland_data.h5'
        self.data_file = h5py.File(self.data_file_name, 'r')


        ### Load data arrays
        #######################################################################

        print "Loading data..."
        print

        # Dictionary of data arrays for each field
        self.data_arrays = {}

        for field in fields:
            self.data_arrays[field] = self.data_file[field][:]

        # Add velocity magnitude to the data
        fields.append('velocity')
        self.v_mag = np.sqrt(self.data_arrays['VX']**2 + self.data_arrays['VY']**2)
        self.data_arrays['velocity'] = self.v_mag

        print "Done."
        print

        # Close file
        self.data_file.close()


        ### Create interpolated data fields
        #######################################################################

        print "Interpolating..."
        print

        # Dictionary of interpolated data fields
        self.interp_fields = {}

        # The color maps have a finer resolution than the actual data, so use
        # the coordinates corresponding to the color map for simplicity

        x_min = 0.
        x_max = 10018.
        y_min = 0.
        y_max = 17946.

        dx = self.data_arrays[fields[0]].shape[1]
        dy = self.data_arrays[fields[0]].shape[0]

        # x and y grid coordinates
        self.x_array = np.linspace(x_min, x_max, dx, endpoint = True)
        self.y_array = np.linspace(y_min, y_max, dy, endpoint = True)

        for field in fields:
            self.interp_fields[field] = RectBivariateSpline(self.x_array, self.y_array,
             np.flipud(self.data_arrays[field]).transpose())

        print "Done."
        print


    # Return interpolated field value at x, y
    def get_field_val(self, field, x, y):
        return self.interp_fields[field]([x], [y], grid=False)[0]
        #return self.interp_fields[field](x, y)[0][0]
