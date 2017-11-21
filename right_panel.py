

import sys
from PyQt4 import QtGui, QtCore


""" Panel on the right side of the main window with buttons and text output. """

class RightPanel(QtGui.QWidget):

    def __init__(self, main_window):

        super(RightPanel, self).__init__()

        # Reference to main parent gui object
        self.main_winddow = main_window
        # Arange stuff vertically
        self.setLayout(QtGui.QVBoxLayout())
        # Maximum width of widgets in side panel
        max_width = 300

        # Drop down list
        self.map_combo = QtGui.QComboBox()
        self.map_combo.addItems(['Velocity', 'Bed', 'Surface', 'Smb', 'Thickness'])
        self.combo_order = ['velocity', 'bed', 'surface', 'smb', 'thickness']
        self.map_combo.setMaximumWidth(max_width)
        self.layout().addWidget(self.map_combo)

        # Plot path button
        self.plot_path_button = QtGui.QPushButton('Plot Path')
        self.plot_path_button.setEnabled(True)
        self.plot_path_button.setMaximumWidth(max_width)
        self.layout().addWidget(self.plot_path_button)

        # Generate mesh button
        self.generate_mesh_button = QtGui.QPushButton('Generate Mesh')
        self.generate_mesh_button.setEnabled(False)
        self.generate_mesh_button.setMaximumWidth(max_width)
        self.layout().addWidget(self.generate_mesh_button)

        # Text output box
        self.text_box = QtGui.QTextBrowser()
        self.text_box.setMaximumWidth(max_width)
        self.layout().addWidget(self.text_box)

        # Set layout width
        self.setMaximumWidth(300 + 12)


    # Respond to a mouse click event by printing the data at the current point
    def print_point_data(self, x, y):
        smb = self.main_winddow.data_loader.get_field_val('smb', x, y)
        thickness = self.main_winddow.data_loader.get_field_val('thickness', x, y)
        surface = self.main_winddow.data_loader.get_field_val('surface', x, y)
        bed = self.main_winddow.data_loader.get_field_val('bed', x, y)
        vx = self.main_winddow.data_loader.get_field_val('VX', x, y)
        vy = self.main_winddow.data_loader.get_field_val('VY', x, y)


        txt = '=================\n' + \
        'x: ' + str(x) + '\n' +\
        'y: ' + str(y) + '\n' +\
        '\nvx: ' +      "{:.3f}".format(vx) + \
        '\nvy: ' +      "{:.3f}".format(vx) + \
        '\nbed: ' +  "{:.3f}".format(bed) + \
        '\nsurf: ' + "{:.3f}".format(surface) + \
        '\nSMB: ' +  "{:.3f}".format(smb) + '\n\n'

        self.text_box.append(txt)
