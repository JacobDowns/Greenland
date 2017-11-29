from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pyqtgraph import LegendItem
from flowline_data import FlowlineData
import numpy as np

"""
Window for plottig a flowline.
"""

class FlowlinePlot(QtGui.QMainWindow):
    def __init__(self, main_window, fg):

        # Main window parent
        self.parent = main_window.main_window
        # flowline graph
        self.fg = fg
        # Create a flowline data object for getting thickness, smb, etc. for the
        # flowline
        self.fd = FlowlineData(main_window, self.fg)

        QtGui.QMainWindow.__init__(self, self.parent)

        self.setWindowTitle('Flowline Plot')
        self.mainWidget = QtGui.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)

        ### Left panel

        self.leftPanelWidget = QtGui.QWidget()

        self.leftPanelLayout = QtGui.QVBoxLayout()
        self.leftPanelWidget.setLayout(self.leftPanelLayout)
        self.plt1 = pg.PlotWidget()
        self.plt2 = pg.PlotWidget()
        self.plt3 = pg.PlotWidget()
        self.leftPanelLayout.addWidget(self.plt1)
        self.leftPanelLayout.addWidget(self.plt2)
        self.leftPanelLayout.addWidget(self.plt3)
        self.legend1 = pg.LegendItem(offset=(-1, 1))
        self.legend2 = pg.LegendItem(offset=(-1, 1))
        self.legend3 = pg.LegendItem(offset=(-1, 1))


        ### Right panel

        self.rightPanelWidget = QtGui.QWidget()
        self.rightPanelLayout = QtGui.QGridLayout()
        self.rightPanelWidget.setLayout(self.rightPanelLayout)

        self.plotButt = QtGui.QPushButton('Plot')
        self.errorLabel = QtGui.QLabel('')
        self.plotButt.clicked.connect(self.plotData)

        self.allCheck        = QtGui.QCheckBox('Plot All')
        self.velocityCheck   = QtGui.QCheckBox('Velocity')
        self.vWidthCheck     = QtGui.QCheckBox('Velocity Width')
        self.smbCheck        = QtGui.QCheckBox('SMB')
        self.surfaceCheck    = QtGui.QCheckBox('Surface')
        self.bedCheck        = QtGui.QCheckBox('Bed')
        self.thicknessCheck  = QtGui.QCheckBox('Thickness')

        self.checkBoxW = QtGui.QWidget()
        self.checkBLayout = QtGui.QVBoxLayout()
        self.checkBoxW.setLayout(self.checkBLayout)
        self.allCheck.setTristate(False)
        self.velocityCheck.setTristate(False)
        self.vWidthCheck.setTristate(False)
        self.smbCheck.setTristate(False)
        self.surfaceCheck.setTristate(False)
        self.bedCheck.setTristate(False)
        self.thicknessCheck.setTristate(False)
        self.allCheck.setCheckState(2)
        self.velocityCheck.setCheckState(2)
        self.vWidthCheck.setCheckState(2)
        self.smbCheck.setCheckState(2)
        self.surfaceCheck.setCheckState(2)
        self.bedCheck.setCheckState(2)
        self.checkBLayout.addWidget(QtGui.QLabel('Plot Checked Data:'))
        self.checkBLayout.addWidget(self.allCheck)
        self.checkBLayout.addWidget(self.velocityCheck)
        self.checkBLayout.addWidget(self.vWidthCheck)
        self.checkBLayout.addWidget(self.smbCheck)
        self.checkBLayout.addWidget(self.surfaceCheck)
        self.checkBLayout.addWidget(self.bedCheck)
        self.checkBLayout.setSpacing(0)
        self.allCheck.stateChanged.connect(self.allCheckChange)

        self.rightPanelLayout.addWidget(self.plotButt,    1, 0, 1, 2)
        self.rightPanelLayout.addWidget(self.checkBoxW,    2, 0, 1, 2)
        self.rightPanelLayout.addWidget(self.errorLabel,  3, 0, 1, 2)
        self.rightPanelLayout.setAlignment(QtCore.Qt.AlignTop)

        self.mainLayout.addWidget(self.leftPanelWidget)
        self.mainLayout.addWidget(self.rightPanelWidget)

        self.legend1.setParentItem(self.plt1.getPlotItem())
        self.legend2.setParentItem(self.plt2.getPlotItem())
        self.legend3.setParentItem(self.plt3.getPlotItem())


        # Pens for each field
        self.pens = {}
        self.pens['velocity'] = pg.mkPen(color=(0, 0, 0), width=2)
        self.pens['bed'] = pg.mkPen(color=(0, 0, 255), width=2)
        self.pens['surface'] = pg.mkPen(color=(255, 255, 255), width=2)
        self.pens['velocity'] = pg.mkPen(color=(100, 0, 0), width=2)
        self.pens['width'] = pg.mkPen(color=(76, 153, 0), width=2)
        self.pens['smb'] = pg.mkPen(color=(76, 153, 0), width=2)

        self.plotData()
        self.show()


    # Clicked on PLot all check box
    def allCheckChange(self, e):
        if self.allCheck.checkState() == 2:
            self.velocityCheck.setCheckState(2)
            self.vWidthCheck.setCheckState(2)
            self.smbCheck.setCheckState(2)
            self.surfaceCheck.setCheckState(2)
            self.bedCheck.setCheckState(2)
        else:
            self.velocityCheck.setCheckState(0)
            self.vWidthCheck.setCheckState(0)
            self.smbCheck.setCheckState(0)
            self.surfaceCheck.setCheckState(0)
            self.bedCheck.setCheckState(0)


    # Plot data
    def plotData(self):
        if self.velocityCheck.checkState() == 2:
            velocityPlt = self.plt2.plot(self.fd.distances, self.fd.flowline_data['velocity'], pen = self.pens['velocity'])
            self.legend2.addItem(velocityPlt, 'Velocity (m / yr)')

        if self.smbCheck.checkState() == 2:
            smbPlt = self.plt2.plot(self.fd.distances, self.fd.flowline_data['smb'], pen = self.pens['smb'])
            self.legend2.addItem(smbPlt, 'SMB(m)')

        if self.surfaceCheck.checkState() == 2:
            surfPlt = self.plt1.plot(self.fd.distances, self.fd.flowline_data['surface'], pen = self.pens['surface'])
            self.legend1.addItem(surfPlt, 'Surface(m)')

        if self.bedCheck.checkState() == 2:
            bedPlt = self.plt1.plot(self.fd.distances, self.fd.flowline_data['bed'], pen = self.pens['bed'])
            self.legend1.addItem(bedPlt, 'Bed(m)')

        if self.vWidthCheck.checkState() == 2:
            vWidthPlt = self.plt3.plot(self.fd.distances, self.fd.flowline_data['width'], pen = self.pens['width'])
            self.legend3.addItem(vWidthPlt, 'Vel. Width(m)')

        pg.QtGui.QApplication.processEvents()
        print 'Plotting done.'
