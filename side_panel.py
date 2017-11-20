

import sys
from PyQt4 import QtGui, QtCore


""" Panel on the right side of the main window with buttons and text output. """

class SidePanel(QtGui.QWidget):

    def __init__(self):
        super(SidePanel, self).__init__()

        self.setLayout(QtGui.QVBoxLayout())

        # Maximum width of widgets in side panel
        max_width = 300

        # Drop down list
        self.map_combo = QtGui.QComboBox()
        self.map_combo.addItems(['Velocity', 'Bed', 'Surface', 'Smb', 'Thickness'])
        self.map_combo.setMaximumWidth(max_width)
        self.layout.addWidget(self.map_combo)

        # Plot path button
        self.plot_path_button = QtGui.QPushButton('Plot Path')
        self.plot_path_button.setEnabled(False)
        self.plot_path_button.setMaximumWidth(max_width)

        # Generate mesh button
        self.generate_mesh_button = QtGui.QPushButton('Generate Mesh')
        self.generate_mesh_button.setEnabled(False)
        self.generate_mesh_button.setMaximumWidth(max_width)

        # Text output box
        self.text_box = QtGui.QTextBrowser()
        self.text_box.setMaximumWidth(max_width)
