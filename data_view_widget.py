

import sys
from PyQt4 import QtGui
from helper_files.classes.ColorBarAnchorWidget import ColorBarAnchorWidget
import pyqtgraph as pg
from flow_integrator import FlowIntegrator
from width_calculator import WidthCalculator
from flowline_plot import FlowlinePlot
from flowline_data import FlowlineData
import numpy as np


""" Widget for viewing data. """

class DataViewWidget(pg.PlotWidget):

    def __init__(self, main_window):

        super(DataViewWidget, self).__init__()

        # Currently displayed field
        self.current_field = 'velocity'
        # Keep ref to main window
        self.main_window = main_window


        ### Create image items for each data field

        fields = ['smb', 'bed', 'surface', 'thickness', 'velocity']

        # Image items, color bars, and color maps for each data field
        self.image_items = {}
        self.cbars = {}


        for field in fields:
            # Load image
            color_data = main_window.color_loader.color_data[field]
            self.image_items[field] = pg.ImageItem(color_data)
            self.image_items[field].setOpts(axisOrder = 'row-major')
            self.image_items[field].setZValue(0)
            # Respond to mouse click event
            self.image_items[field].mouseClickEvent = main_window.mouseClick

            # Load color bar
            cmap, cbar = main_window.color_loader.get_cmap_cbar(field)
            self.cbars[field] = cbar

        # Set displayed field
        self.addItem(self.image_items[self.current_field])


        ### Setup the plot widget

        # Set some options of the plot widget
        self.setAspectLocked(True)

        # Create a widget that will anchor the color bar in the top right corner
        self.cbar_anchor = ColorBarAnchorWidget()
        self.cbar_anchor.hideAxis('left')
        self.cbar_anchor.hideAxis('bottom')
        self.cbar_anchor.addItem(self.cbars[self.current_field])
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
        # Mouse move event
        self.getViewBox().hoverEvent = main_window.mouseMove


        ### Flow line stuff

        # List of flowlines
        self.flowlines = []
        # Pen for flow line drawing
        self.flowline_pen =  pg.mkPen(color=(255, 0, 0), width=2)
        # Object for integrating velocity field along flowline
        self.flow_integrator = FlowIntegrator(self.main_window.data_loader)


        ### Flow region stuff
        self.flowline_graphs = []


    ### Set the displayed data field
    def setField(self, field):
        if not field == self.current_field:
            self.removeItem(self.image_items[self.current_field])
            self.removeItem(self.cbars[self.current_field])
            self.current_field = field
            self.addItem(self.image_items[self.current_field])
            self.addItem(self.cbars[self.current_field])


    ### Add a flowline
    def addFlowline(self, x, y):
        x_interp, y_interp = self.flow_integrator.integrate(x, y)
        self.flowlines.append((x_interp, y_interp))

        ts = np.linspace(0., 1., 1500)
        flowline = pg.PlotDataItem(x_interp(ts), y_interp(ts), pen = self.flowline_pen)
        flowline.setZValue(1)
        self.addItem(flowline)


        if len(self.flowlines) == 3:
            xc = self.flowlines[0][0]
            yc = self.flowlines[0][1]
            xb1 = self.flowlines[1][0]
            yb1 = self.flowlines[1][1]
            xb2 = self.flowlines[2][0]
            yb2 = self.flowlines[2][1]

            width_calculator = WidthCalculator(xc, yc, xb1, yb1, xb2, yb2)
            fg = width_calculator.get_width()
            fg.setZValue(1)
            self.addItem(fg)
            self.flowline_graphs.append(fg)


    ### Mouse click event
    def mouseClick(self):
        for g in self.flowline_graphs:
            g.offPointClick()


    ### ctrl key pressed
    def ctrlKeyPressed(self):
        for g in self.flowline_graphs:
            g.ctrl_pressed = True


    ### ctrl key released
    def ctrlKeyReleased(self):
        for g in self.flowline_graphs:
            g.ctrl_pressed = False


    ### del key released
    def delKeyPressed(self):
        for g in self.flowline_graphs:
            g.deleteKeyPressed()


    ### e key pressed
    def eKeyPressed(self):
        for g in self.flowline_graphs:
            g.extendKeyPressed()


    ### s key pressed
    def sKeyPressed(self):
        for g in self.flowline_graphs:
            g.subdivideKeyPressed()


    ### Mouse move event
    def mouseMove(self, ev):
        for g in self.flowline_graphs:
            g.mouseMove(self.getViewBox().mapToView(ev.pos()))


    ### Plot path button clicked
    def plotPathClicked(self):
        if len(self.flowline_graphs) > 0:
            plot = FlowlinePlot(self.main_window, self.flowline_graphs[0])



    # Generate mesh button
    def generateMeshClicked(self):
        if len(self.flowline_graphs) > 0:
            file_name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
                'File Name (meshes/)')

            if ok:
                if file_name == '':
                    file_name = 'mesh'

                file_name += '.h5'

                # Get flowline data
                fd = FlowlineData(self.main_window, self.flowline_graphs[0])
                fd.generate_mesh()
                print fd
