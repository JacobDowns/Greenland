import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class FlowlineGraph(pg.GraphItem):
    def __init__(self):
        self.dragPoint = None
        self.dragOffset = None
        pg.GraphItem.__init__(self)
        self.num_points = 0

    def setData(self, **kwds):
        self.data = kwds

        # We need two fields in
        # Check to make sure we got all required fields
        cond1 = 'xc' in kwds and 'yc' in kwds
        cond2 = 'xb1' in kwds and 'yb1' in kwds
        cond3 = 'xb2' in kwds and 'yb2' in kwds

        if cond1 and cond2 and cond3:

            print "safd"

            xs = self.data.pop('xc')
            ys = self.data.pop('yc')
            xb1 = self.data.pop('xb1')
            yb1 = self.data.pop('yb1')
            xb2 = self.data.pop('xb2')
            yb2 = self.data.pop('yb2')

            self.num_points = len(xs)

            pos_xs = np.concatenate([xs, xb1, xb2])
            pos_ys = np.concatenate([ys, yb1, yb2])
            pos = np.array([pos_xs, pos_ys]).transpose()

            print pos
            self.data['pos'] = pos

            indexes = np.array(range(self.num_points), dtype = int)
            from_indexes = np.concatenate([indexes, indexes, indexes[1:]])
            to_indexes = np.concatenate([indexes + self.num_points, indexes + 2*self.num_points, indexes[:-1]])
            adj = np.array([from_indexes, to_indexes]).transpose()
            self.data['adj'] = adj

            print
            print adj


            self.data['data'] = np.empty(3*self.num_points, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(3*self.num_points)

            self.updateGraph()

    def updateGraph(self):
        print self.data
        pg.GraphItem.setData(self, **self.data)
