

import sys
from PyQt4 import QtGui
from helper_files.classes.ColorBarAnchorWidget import ColorBarAnchorWidget
import pyqtgraph as pg


""" Widget for viewing data. """

class DataViewWidget(pg.PlotWidget):

    def __init__(self, color_loader, field):

        super(DataViewWidget, self).__init__()

        # Color data for display
        self.color_data = color_loader.color_data[field]

        # Set some options of the plot widget
        self.setAspectLocked(True)
        #self.invertY(True)

        # Image item for displaying the data
        self.image_item = pg.ImageItem(self.color_data)
        self.image_item.setOpts(axisOrder = 'row-major')
        self.addItem(self.image_item)

        # Get the color map / color bar
        self.cmap, self.cbar = color_loader.get_cmap_cbar(field)

        # Create a widget that will anchor the color bar in the top right corner
        self.cbar_anchor = ColorBarAnchorWidget()
        self.cbar_anchor.hideAxis('left')
        self.cbar_anchor.hideAxis('bottom')
        self.cbar_anchor.addItem(self.cbar)
        self.addItem(self.cbar_anchor)
        self.cbar_anchor.setFixedWidth(158)
        self.cbar_anchor.setFixedHeight(250)
        self.cbar_anchor.setAspectLocked(True)
        self.cbar_anchor.getViewBox().setRange(xRange = [-64.0, 114], yRange = [-15, 247], padding = 0.0)
        self.cbar_anchor.invertY(True)
        self.cbar_anchor.setParentItem(self.getPlotItem())
        self.cbar_anchor.getViewBox().setMouseEnabled(x = False, y = False)
        self.cbar_anchor.anchor(itemPos = (1, 0), parentPos=(1, 0), offset = (-10, -10))

        # Set view ranges
        self.getViewBox().setRange(xRange=[0, 10018], yRange=[0, 17964], padding=0.1)
