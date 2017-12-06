

import sys
from PyQt4 import QtGui
from gui.colorbar_anchor_widget import ColorBarAnchorWidget
import pyqtgraph as pg
from utility.flow_integrator import FlowIntegrator
from utility.width_calculator import WidthCalculator
from gui.flowline_plot import FlowlinePlot
from utility.flowline_data import FlowlineData
from gui.flowline_path import FlowlinePath
import numpy as np


""" Widget where data is displayed. """

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
        xs, ys, ts = self.flow_integrator.integrate(x, y)
        flowline = FlowlinePath()
        flowline.setData(x = xs, y = ys, symbolSize = 18., pxMode = True, pen = self.flowline_pen)
        flowline.selectFlowline = self.selectFlowline
        flowline.setZValue(1)

        self.flowlines.append(flowline)
        self.addItem(flowline)


    ### Mouse click event
    def mouseClick(self):
        for f in self.flowlines:
            f.offPointClick()

        for g in self.flowline_graphs:
            g.offPointClick()


    ### ctrl key pressed
    def ctrlKeyPressed(self):
        for f in self.flowlines:
            f.ctrl_pressed = True

        for g in self.flowline_graphs:
            g.ctrl_pressed = True


    ### ctrl key released
    def ctrlKeyReleased(self):
        for f in self.flowlines:
            f.ctrl_pressed = False

        for g in self.flowline_graphs:
            g.ctrl_pressed = False


    ### del key released
    def delKeyPressed(self):
        for f in self.flowlines:
            f.deleteKeyPressed()

        for g in self.flowline_graphs:
            g.deleteKeyPressed()


    ### e key pressed
    def eKeyPressed(self):
        for f in self.flowlines:
            f.extendKeyPressed()

        for g in self.flowline_graphs:
            g.extendKeyPressed()


    ### s key pressed
    def sKeyPressed(self):
        for f in self.flowlines:
            f.subdivideKeyPressed()

        for g in self.flowline_graphs:
            g.subdivideKeyPressed()


    ### Mouse move event
    def mouseMove(self, ev):

        for f in self.flowlines:
            f.mouseMove(self.getViewBox().mapToView(ev.pos()))

        for g in self.flowline_graphs:
            g.mouseMove(self.getViewBox().mapToView(ev.pos()))


    ### Function called by a flowline path when one of it's points is clicked on
    ### or dragged. Deselects all points in other flowlines
    def selectFlowline(self, flowline):
        for g in self.flowlines:
            if not flowline == g:
                g.deselectAll()
                g.updateGraph()


    ### Plot path button clicked
    def plotPathClicked(self):
        if len(self.flowline_graphs) > 0:
            plot = FlowlinePlot(self.main_window, self.flowline_graphs[0])


    ### Flowline graph button clicked
    def flowlineGraphClicked(self):
        if len(self.flowlines) == 3:
            resolution, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
                'Resolution (m)')

            if ok:
                if resolution == '':
                    1000.0

                # If there are 3 flowlines, create a flowline graph
                cxs = self.flowlines[0].data['x']
                cys = self.flowlines[0].data['y']
                bxs1 = self.flowlines[1].data['x']
                bys1 = self.flowlines[1].data['y']
                bxs2 = self.flowlines[2].data['x']
                bys2 = self.flowlines[2].data['y']

                wc = WidthCalculator(cxs, cys, bxs1, bys1, bxs2, bys2, float(resolution))
                fg = wc.get_width()
                fg.setZValue(1)
                self.addItem(fg)
                self.flowline_graphs.append(fg)

                for f in self.flowlines:
                    f.data['symbolSize'] = 0.
                    f.updateGraph()

                self.flowlines = []


    ### Generate mesh button clicked
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
                fd.write_data(str(file_name))
        i
