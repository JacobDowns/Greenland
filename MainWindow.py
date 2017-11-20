
from PyQt4 import QtCore, QtGui


""" Main GUI window. """

class MainWindow():
    def __init__(self):
        # Create application
        self.app = QtGui.QApplication([])

        # Main window
        self.main_window = QtGui.QMainWindow()
        self.main_window.setWindowTitle('Greenland')
        self.main_window.setMinimumHeight(1000)
        self.main_window.setMinimumWidth(1200)
        self.main_window.showMaximized()

        # Central widget in main window
        self.main_widget = QtGui.QWidget()
        self.main_window.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(QtGui.QHBoxLayout())
        iiContainer = QtGui.QStackedWidget()    # STACKED WIDGET (inside the layout)

#####################################################
####      SIDE WIDGET WITH BUTTONS               ####
#####################################################

buttonBoxWidget = QtGui.QWidget()
buttonBox = QtGui.QVBoxLayout()
buttonBoxWidget.setLayout(buttonBox)

mapList = QtGui.QComboBox()
maps = ['Velocity', 'Bed', 'Surface', 'Smb', 'Thickness']#, 'OldThickness']
mapList.addItems(maps)


instructionButton = QtGui.QPushButton('Instructions')
clearButton      = QtGui.QPushButton('Clear Points')

cProfButton      = QtGui.QPushButton('Plot Path') #FIXME should automatically get profile
cProfButton.setEnabled(False)
meshButton       = QtGui.QPushButton('Generate Mesh')
meshButton.setEnabled(False)

mouseCoordinates = QtGui.QLabel('x:\ty:')
textOut = QtGui.QTextBrowser()

maxWidth = 300

mapList.setMaximumWidth(maxWidth)
instructionButton.setMaximumWidth(maxWidth)
clearButton.setMaximumWidth(maxWidth)
clearButton.setMaximumWidth(maxWidth)
cProfButton.setMaximumWidth(maxWidth)
meshButton.setMaximumWidth(maxWidth)
textOut.setMaximumWidth(maxWidth)


buttonBox.addWidget(mapList)
buttonBox.addWidget(instructionButton)
buttonBox.addWidget(clearButton)
buttonBox.addWidget(cProfButton)
buttonBox.addWidget(meshButton)
buttonBox.addWidget(textOut)


#####################################################
####         CREATE BOTTOM PLOT                  ####
#####################################################
# bp = pg.PlotWidget()
# bpLegend = bp.getPlotItem().addLegend()

# iiContainer.setMinimumHeight(mw.height()*(2/3))

lsw = QtGui.QWidget()
leftSide = QtGui.QVBoxLayout()
lsw.setLayout(leftSide)
leftSide.addWidget(iiContainer)
# leftSide.addWidget(bp,1)


mainLayout.addWidget(lsw)
mainLayout.addWidget(buttonBoxWidget)
buttonBoxWidget.setMaximumWidth(maxWidth + 12)

mw.show()

"""
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()

imagedata = np.random.random((256,256))
imv.setImage(imagedata)
imv.ui.histogram.hide()"""

import sys
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
