import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

w = pg.GraphicsWindow()
w.setWindowTitle('pyqtgraph example: CustomGraphItem')
v = w.addViewBox()
v.setAspectLocked()

class Graph(pg.GraphItem):
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

            self.data['pos'] = pos

            indexes = np.array(range(self.num_points), dtype = int)
            from_indexes = np.concatenate([indexes, indexes, indexes[1:]])
            to_indexes = np.concatenate([indexes + self.num_points, indexes + 2*self.num_points, indexes[:-1]])
            adj = np.array([from_indexes, to_indexes]).transpose()
            self.data['adj'] = adj


            self.data['data'] = np.empty(3*self.num_points, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(3*self.num_points)

            print
            print self.data
            print 

            self.updateGraph()

    ### Respond to a mouse drag
    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            # We are already one step into the drag. Find the point(s) at the mouse
            # cursor when the button was first pressed:
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)

            if len(pts) == 0:
                ev.ignore()
                return

            # Index of point being dragged
            self.drag_point_index = pts[0].data()
            # Point to drag to
            self.drag_offset_x = self.data_dict['x'][self.drag_point_index] - pos.x()
            self.drag_offset_y = self.data_dict['y'][self.drag_point_index] - pos.y()
            # Select this point
            self.deselectAll()
            self.addSelectedPoint(self.drag_point_index)

        elif ev.isFinish():
            self.drag_point_index = None
            return
        else:
            if self.drag_point_index is None:
                ev.ignore()
                return

        ### In the midst of a drag

        # Set position of dragged point
        px = ev.pos().x() + self.drag_offset_x
        py = ev.pos().y() + self.drag_offset_y
        self.setPointCoords(self.drag_point_index, px, py)
        self.updateData()

        ev.accept()

    def updateGraph(self):
        print self.data
        pg.GraphItem.setData(self, **self.data)


g = Graph()
v.addItem(g)

## Define positions of nodes
xc = np.array([-0.5, 0., 0.5])
yc = np.array([0.,   0., 0.])

xb1 = xc[:]
yb1 = yc + 0.5

xb2 = xc[:]
yb2 = yc - 0.5

g.setData(xc=xc, yc=yc, xb1=xb1, yb1=yb1, xb2=xb2, yb2=yb2, size = 25., pxMode = True)




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
