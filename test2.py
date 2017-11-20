import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
w = pg.GraphicsWindow()
w.setWindowTitle('thing')
v = w.addViewBox()
v.setRange(xRange = [-1., 1.], yRange = [-1., 1.], padding = 0.0)
v.setAspectLocked()

class CustomDataItem(pg.PlotDataItem):
    def __init__(self):
        self.dragPoint = None
        self.dragOffset = None
        self.highlight_pen = pg.mkPen(pg.mkColor('r'))
        self.default_pen = default_pen = pg.mkPen(pg.mkColor('w'))
        self.selected_index = None
        pg.PlotDataItem.__init__(self)
        #self.mouseClickEvent = self.on_click
        self.scatter.sigClicked.connect(self.on_click)


    def setData(self, **kwds):
        if 'x' in kwds:
            self.data_xs = kwds['x']
        if 'y' in kwds:
            self.data_ys = kwds['y']
        if 'symbolPen' in kwds:
            self.symbol_pens = kwds['symbolPen']

        #print kwds

        pg.PlotDataItem.setData(self, **kwds)



    def updateGraph(self):
        pg.PlotDataItem.setData(self, **self.data)
        for i,item in enumerate(self.textItems):
            item.setPos(*self.data['pos'][i])


    def shape(self):
        # Inherit shape from the curve item
        return self.scatter.shape()

    def boundingRect(self):
        # All graphics items require this method (unless they have no contents)
        return self.shape().boundingRect()

    def paint(self, p, *args):
        # All graphics items require this method (unless they have no contents)
        return


    def mouseDragEvent(self, ev):
        print "sf"

        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first
            # pressed:
            pos = ev.buttonDownPos()
            #print pos
            #quit()
            #print "pos", pos
            pts = self.scatter.pointsAt(pos)

            if len(pts) == 0:
                ev.ignore()
                return

            self.dragPoint = pts[0]
            ind = pts[0].data()
            self.drag_offset_x = self.data_xs[ind] - pos.x()
            self.drag_offset_y = self.data_ys[ind] - pos.y()
        elif ev.isFinish():
            #print "asdf"
            self.dragPoint = None
            return
        else:
            #print "there"
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()
        self.selected_index = ind
        #self.symbols[ind] =
        self.data_xs[ind] = ev.pos().x() + self.drag_offset_x
        self.data_ys[ind] = ev.pos().y() + self.drag_offset_y
        symbol_pens = [self.default_pen for i in range(len(self.symbol_pens))]
        symbol_pens[ind] = self.highlight_pen

        #self.symbol_pens[ind] = self.highlight_pen
        self.setData(x = self.data_xs, y = self.data_ys, symbolPen = symbol_pens)
        ev.accept()


    # A click not on a a point
    def off_click(self, pos):
        symbol_pens = [self.default_pen for i in range(len(self.symbol_pens))]
        self.selected_index = None
        self.setData(x = self.data_xs, y = self.data_ys, symbolPen = symbol_pens)

    def on_click(self, point, pts):
        #print point.data()
        ind = pts[0].data()
        print ind
        symbol_pens = [self.default_pen for i in range(len(self.symbol_pens))]
        symbol_pens[ind] = self.highlight_pen
        print symbol_pens
        self.selected_index = ind
        self.setData(x = self.data_xs, y = self.data_ys, symbolPen = symbol_pens)




g = CustomDataItem()
data_xs = np.array([0., 0.1, 0.5])
data_ys = np.array([0., 0.5, 0.])

default_pen = pg.mkPen(pg.mkColor('w'))
highlight_pen = pg.mkPen(pg.mkColor('r'))
symbol_pens = [default_pen, default_pen, default_pen]

g.setData(x = data_xs, y = data_ys, symbolSize = 25., data = range(3), symbolPen = symbol_pens, pxMode = True)
v.addItem(g)

def mouse_click(e):
    pos = e.pos()
    pts = g.off_click(pos)


def thing(e):
    print e

w.keyboardGrabber()


w.keyPressEvent = thing
w.keyReleaseEvent = thing




v.mouseClickEvent = mouse_click

print dir(v)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
