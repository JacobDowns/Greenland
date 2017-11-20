
from PyQt4 import QtCore, QtGui
from main_panel import *
from right_panel import *
from data_view_widget import *
from data_loader import *

""" Main GUI window. """

class MainWindow():

    def __init__(self):

        # Load the data
        self.data_loader = DataLoader()

        # Create application
        self.app = QtGui.QApplication([])

        # Main window
        self.main_window = QtGui.QMainWindow()
        self.main_window.setWindowTitle('Greenland')
        self.main_window.setMinimumHeight(1000)
        self.main_window.setMinimumWidth(1200)
        self.main_window.showMaximized()

        # Central widget in main window with hbox layout
        self.main_widget = QtGui.QWidget()
        self.main_window.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(QtGui.QHBoxLayout())

        # Add main panel (where stuff is plotted)
        self.main_panel = MainPanel(self)
        self.main_widget.layout().addWidget(self.main_panel)

        # Add right panel (with drop down box, buttons, text box)
        self.right_panel = RightPanel(self)
        self.main_widget.layout().addWidget(self.right_panel)


        ### Event handling

        # Change selection in drop down box
        self.right_panel.map_combo.currentIndexChanged.connect(self.change_field)

        # Register keypress / release
        self.key_pressed = {}
        self.key_pressed['ctrl'] = False
        self.key_pressed['shift'] = False
        self.main_widget.keyboardGrabber()
        self.main_widget.keyPressEvent = self.key_press
        self.main_widget.keyReleaseEvent = self.key_release

        self.main_window.show()


    # Change the data field displayed in the main panel
    def change_field(self, index):
        field = self.right_panel.combo_order[index]
        self.main_panel.set_field(field)


    # Key press event
    def key_press(self, e):
        if e.key() == 16777248:
            self.key_pressed['shift'] = True
        elif e.key() == 16777249:
            self.key_pressed['ctrl'] = True

        print self.key_pressed

    # Key release
    def key_release(self, e):
        if e.key() == 16777248:
            self.key_pressed['shift'] = False
        elif e.key() == 16777249:
            self.key_pressed['ctrl'] = False

        print self.key_pressed


    def mouse_click(self, e):
        x = e.pos().x()
        y = e.pos().y()

        # ctrl + click
        if self.key_pressed['shift']:
            self.main_panel.display_flowline(x, y)
        else:
            self.right_panel.print_point_data(x, y)


mw = MainWindow()

import sys
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
