

import sys
from PyQt4 import QtGui, QtCore
from data_view_widget import *
from color_data_loader import *
from flow_integrator import *
from width_calculator import *
import pyqtgraph as pg

"""
Main panel where stuff is plotted. Extends a Qstacked widget, which allows
switching between data sets in different widgets.
"""

class MainPanel(QtGui.QStackedWidget):

    def __init__(self, main_window):

        super(MainPanel, self).__init__()

        # Reference to main parent gui object
        self.main_window = main_window
        # Load color data
        self.color_loader = ColorDataLoader()
        # Data loader
        self.data_loader = self.main_window.data_loader
        # Stores data view panels for each data field
        self.data_view_panels = {}
        # List of data field names
        self.fields = self.color_loader.fields
        # List of flowlines
        self.flow_lines = []

        for field in self.fields:
            print field
            self.data_view_panels[field] = DataViewWidget(self.color_loader, field)
            self.addWidget(self.data_view_panels[field])
            self.data_view_panels[field].image_item.mouseClickEvent = self.main_window.mouse_click

        # Dsiplay velocity first
        self.set_field('velocity')

        ### Stuff for flowline integration

        # Pen for flow line drawing
        self.flow_line_pen =  pg.mkPen(color=(255, 255, 255), width=2)
        # Object for integrating velocity field along flowline
        self.flow_integrator = FlowIntegrator(self.data_loader)


    # Set the currently displayed data field
    def set_field(self, field):
        self.current_field = field
        self.setCurrentWidget(self.data_view_panels[field])
        

    # Draw a flowline
    def display_flowline(self, x, y):
        x_interp, y_interp = self.flow_integrator.integrate(x, y)
        self.flow_lines.append((x_interp, y_interp))

        ts = np.linspace(0., 1., 1500)
        flow_line = pg.PlotDataItem(x_interp(ts), y_interp(ts)) # pen = self.flow_line_pen)
        self.currentWidget().addItem(flow_line)


        if len(self.flow_lines) == 3:
            xc = self.flow_lines[0][0]
            yc = self.flow_lines[0][1]
            xb1 = self.flow_lines[1][0]
            yb1 = self.flow_lines[1][1]
            xb2 = self.flow_lines[2][0]
            yb2 = self.flow_lines[2][1]

            width_calculator = WidthCalculator(xc, yc, xb1, yb1, xb2, yb2)
            fg = width_calculator.get_width()
            self.currentWidget().addItem(fg)
            #width_calculator.calc_width()
