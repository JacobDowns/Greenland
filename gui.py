
from PyQt4 import QtCore, QtGui


""" Main GUI window. """

class GUI():
    def __init__(self):
        self.app = QtGui.QApplication([])
        self.mw = QtGui.QMainWindow()
        self.mw.setWindowTitle('Greenland')
        self.mw.setMinimumHeight(1000)
        self.mw.setMinimumWidth(1200)
        self.mw.showMaximized()
        cw = QtGui.QWidget()            # GENERIC WIDGET AS CENTRAL WIDGET (inside main window)
        mw.setCentralWidget(cw)
        mainLayout = QtGui.QHBoxLayout()
        cw.setLayout(mainLayout)
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
# buttonBox.addWidget(mouseCoordinates)


# LABELS AND LINE EDITS
# time_widget    = QtGui.QWidget()
#
# time_container = QtGui.QGridLayout()
# time_widget.setLayout(time_container)
#

"""
spatialInputWidget = QtGui.QWidget()
uh = QtGui.QHBoxLayout()
spatialInputWidget.setLayout(uh)
model_res_label    = QtGui.QLabel('Sptl res(m):')
model_res_lineEdit = QtGui.QLineEdit('2000')"""
# uh.addWidget(model_res_lineEdit)
# uh.addWidget(model_res_lineEdit)

#
# t_end_label    = QtGui.QLabel('t_end(yr):')
# t_end_lineEdit = QtGui.QLineEdit('20000')
#
# t_step_label    = QtGui.QLabel('t_step(yr):')
# t_step_lineEdit = QtGui.QLineEdit('10')
# t_current = QtGui.QLabel('Current year: ')
#
# time_container.addWidget(model_res_label,    0, 0)
# time_container.addWidget(model_res_lineEdit, 0, 1)
# time_container.addWidget(t_end_label,        1, 0)
# time_container.addWidget(t_end_lineEdit,     1, 1)
# time_container.addWidget(t_step_label,       2, 0)
# time_container.addWidget(t_step_lineEdit,    2, 1)
# time_container.addWidget(t_current,          3, 0, 1, 2)
#
# buttonBox.addWidget(time_widget)

# buttonBox.addWidget(spatialInputWidget)
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
