
from PyQt4 import QtCore, QtGui
import h5py
import pyqtgraph as pg
from gui.colorbar import *

""" Object for loading and color data and building color bars / map data for each field. """

class ColorDataLoader():

    def __init__(self):

        # Data fields
        fields = ['smb', 'bed', 'surface', 'thickness', 'velocity']
        self.fields = fields

        # File with color maps
        self.color_file_name = './data/color_data.h5'
        self.color_file = h5py.File(self.color_file_name, 'r')


        ### Load color data for each field
        #######################################################################

        print "Loading color data..."
        print

        # Dictionary of data arrays
        self.color_data = {}

        for field in fields:
            self.color_data[field] = np.flipud(self.color_file[field][:])

        print "Done."
        print


        ### Create color map data for each field
        #######################################################################

        print "Loading color map data..."
        print

        # Dictionaries for storing color map data for each field
        self.cmap_p = {}
        self.cmap_c = {}

        for field in fields:
            self.cmap_p[field] = self.color_file[field + '_cmap_p'][:]
            self.cmap_c[field] = self.color_file[field + '_cmap_c'][:].astype(int)


        print "Done."
        print

        # Close file
        self.color_file.close()


    # Return the colormap / colorbar for a given field
    def get_cmap_cbar(self, field):
        cbar_height = 200
        cbar_width = 20
        cmap = pg.ColorMap(self.cmap_p[field], self.cmap_c[field], mode='byte')
        cbar = None

        if field == 'velocity':
            cbar = LogColorBar(cmap, cbar_width, cbar_height,
                                 label='Velocity(m/yr)',
                                 tick_labels=['0', '10', '100', '1,000', '8,000'],
                                 ticks=[0, 10, 100, 1000, 8000])
        elif field == 'bed':
            cbar = ColorBar(cmap, cbar_width, cbar_height,
                              label='Bed Ele.(m)',
                              tick_labels=['-5,000','-4,000','-3,000','-2,000','-1,000','0', '1,000', '2,000', '3,000', '3,500'],
                              ticks=[-5000,-4000,-3000,-2000,-1000,0, 1000, 2000, 3000, 3500])
        elif field == 'surface':
            cbar = ColorBar(cmap, cbar_width, cbar_height,
                              label='Surface Ele.(m)',
                              tick_labels=['0', '500', '1,000', '1,500', '2,000', '2,500', '3,000', '3,500'],
                              ticks=[0, 500, 1000, 1500, 2000, 2500, 3000, 3500])
        elif field == 'smb':
            cbar = ColorBar(cmap, cbar_width, cbar_height,
                              label='SMB(m)',
                              tick_labels=['-11', '0',  '6'],
                              ticks=[-11000, 0, 6000],
                              name='smb')
        elif field == 'thickness':
            cbar = ColorBar(cmap, cbar_width, cbar_height,
                              label='Thickness(m)',
                              tick_labels=['0', '500', '1000', '1500', '2000', '2500', '3000', '3500'],
                              ticks=[0, 500, 1000, 1500, 2000, 2500, 3000, 3500])

        return cmap, cbar
