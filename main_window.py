
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
        self.color_loader = ColorDataLoader()

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
        self.main_panel = DataViewWidget(self)
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
        self.key_pressed['e'] = False
        self.key_pressed['s'] = False
        self.main_widget.keyboardGrabber()
        self.main_widget.keyPressEvent = self.keyPress
        self.main_widget.keyReleaseEvent = self.keyRelease

        self.main_window.show()


    # Change the data field displayed in the main panel
    def change_field(self, index):
        field = self.right_panel.combo_order[index]
        self.main_panel.setField(field)


    # Key press event
    def keyPress(self, e):
        if e.key() == 69:
            self.key_pressed['e'] = True
            self.main_panel.eKeyPressed()
        if e.key() == 16777248:
            self.key_pressed['shift'] = True
        elif e.key() == 16777249:
            self.key_pressed['ctrl'] = True
            self.main_panel.ctrlKeyPressed()
        elif e.key() == 16777223:
            self.key_pressed['del'] = True
            self.main_panel.delKeyPressed()
        elif e.key() == 83:
            self.key_pressed['s'] = True
            self.main_panel.sKeyPressed()

        print self.key_pressed


    # Key release
    def keyRelease(self, e):
        if e.key() == 69:
            self.key_pressed['e'] = False
        if e.key() == 16777248:
            self.key_pressed['shift'] = False
        elif e.key() == 16777249:
            self.key_pressed['ctrl'] = False
            self.main_panel.ctrlKeyReleased()
        elif e.key() == 16777223:
            self.key_pressed['del'] = False
        elif e.key() == 83:
            self.key_pressed['s'] = False

        print self.key_pressed



    # Mouse click event
    def mouseClick(self, ev):
        x = ev.pos().x()
        y = ev.pos().y()

        if self.key_pressed['shift']:

            self.main_panel.addFlowline(x,y)
        else :
            self.main_panel.mouseClick()


    # Mouse move event
    def mouseMove(self, ev):
        if not ev.isExit():
            self.main_panel.mouseMove(ev)


    # Plot path button in right panel clicked
    def plotPathClicked(self, ev):
        self.main_panel.plotPathClicked()


    # Generate mesh button
    def generateMeshClicked(self, ev):
        self.main_panel.generateMeshClicked()





mw = MainWindow()

import sys
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
