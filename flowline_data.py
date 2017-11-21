import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class FlowlineData():

    def __init__(self, main_window, xs, ys):
        # Ref to main window
        self.main_window = main_window
        # x,y flowline coords
        self.xs = xs
        self.ys = ys


        ### 
