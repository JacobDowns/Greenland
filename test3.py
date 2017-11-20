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
        ### Setup

        # Point data dictionary
        self.data_dict = {}
        # Reference to point being dragged
        self.drag_point = None
        # How much to translate that point by
        self.drag_offset = None
        # Pen for highlighted pint
        self.highlight_pen = pg.mkPen(pg.mkColor('r'))
        # Pen for default points
        self.default_pen = default_pen = pg.mkPen(pg.mkColor('w'))
        # Number of points
        self.num_points = 0
        # Index of selected point
        self.selected_index = None
        # Extend mode?
        self.extend_mode = False
        # Moving point
        self.moving_point_index = None

        pg.PlotDataItem.__init__(self)

        ### Event handling

        # Triggered when a point is clicked
        self.scatter.sigClicked.connect(self.point_clicked)


    ### Set the point data
    def setData(self, **kwds):
        self.data_dict = kwds

        if 'x' in self.data_dict:
            # Get the number of data points
            self.num_points = self.data_dict['x'].shape[0]
            # Data associated with each point is just an index used as an id
            self.data_dict['data'] = range(self.num_points)
            # Pens for each point
            self.data_dict['symbolPen'] = [self.default_pen for i in range(self.num_points)]

        self.updateData()


    ### Adds a point at beginning of path
    def addPointStart(self, x, y):
        self.num_points += 1
        self.data_dict['x'] = np.insert(self.data_dict['x'], 0, x)
        self.data_dict['y'] = np.insert(self.data_dict['y'], 0, y)
        self.data_dict['data'] = range(self.num_points)
        self.data_dict['symbolPen'].append(self.default_pen)
        self.updateData()


    ### Adds a point at end of path
    def addPointEnd(self, x, y):
        self.num_points += 1
        self.data_dict['x'] = np.append(self.data_dict['x'], x)
        self.data_dict['y'] = np.append(self.data_dict['y'], y)
        self.data_dict['data'] = range(self.num_points)
        self.data_dict['symbolPen'].append(self.default_pen)
        self.updateData()


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

            # Point being dragged
            self.drag_point = pts[0]
            # Index of dragged point
            ind = pts[0].data()
            # Point to drag to
            self.drag_offset_x = self.data_dict['x'][ind] - pos.x()
            self.drag_offset_y = self.data_dict['y'][ind] - pos.y()

            self.setSelectedPoint(ind)

        elif ev.isFinish():
            self.drag_point = None
            return
        else:
            if self.drag_point is None:
                ev.ignore()
                return

        ### In the midst of a drag

        # Set position of dragged point
        self.data_dict['x'][self.selected_index] = ev.pos().x() + self.drag_offset_x
        self.data_dict['y'][self.selected_index] = ev.pos().y() + self.drag_offset_y
        # Highlight the dragged point
        self.data_dict['symbolPen'][self.selected_index] = self.highlight_pen

        self.updateData()

        ev.accept()


    ### Indicates a point is selected by usnig a different pen
    def setSelectedPoint(self, index):
        # If there is a selected point already, unselect it
        self.deselect()
        # Select the new point
        self.selected_index = index
        self.data_dict['symbolPen'][self.selected_index] = self.highlight_pen


    ### Deselect the currently selected point
    def deselect(self):
        if not self.selected_index == None:
            self.data_dict['symbolPen'][self.selected_index] = self.default_pen
            self.selected_index = None


    ### Triggers when e key is pressed for extend mode
    def extendKeyPressed(self):

        # If the first point is selected and we're not in extend mode, trigger extend mode
        if (not self.extend_mode) and (self.selected_index == 0 or self.selected_index == self.num_points - 1):
            # Enable extend mode
            self.setExtendMode(True)

            # If selected point is at beginning of path, add point starting from
            # there. If selected point is at end, start it from there.
            if self.selected_index == 0:
                self.addPointStart(*self.getPointCoords(self.selected_index))
                self.moving_point_index = 0
            else :
                self.addPointEnd(*self.getPointCoords(self.selected_index))
                self.moving_point_index = self.num_points - 1

        else :
            self.setExtendMode(False)


    ### Dumb setter function for extend mode
    def setExtendMode(self, mode):
        self.extend_mode = mode
        print "extend mode", self.extend_mode


    ### Respond to an off point click event
    def offPointClick(self):
        self.setExtendMode(False)
        self.deselect()
        self.updateData()


    ### Point click event: highlight the clicked point
    def point_clicked(self, p, pts):
        if self.extend_mode:
            if self.selected_index == 0:
                self.addPointStart(*self.getPointCoords(self.selected_index))
            else :
                self.addPointEnd(*self.getPointCoords(self.selected_index))
                self.moving_point_index += 1

        self.setSelectedPoint(pts[0].data())
        self.updateData()


    ### Get point coordinates
    def getPointCoords(self, index):
        return self.data_dict['x'][index], self.data_dict['y'][index]


    ### Set point coordinates
    def setPointCoords(self, index, x, y):
        self.data_dict['x'][index] = x
        self.data_dict['y'][index] = y


    ### Respond to mouse movement
    def mouseMove(self, x, y):
        # Check if we're in extend mode
        if self.extend_mode:
            # Move the first or last point to mouse coordinates
            self.setPointCoords(self.moving_point_index, x, y)
            self.updateData()



    ### Respond to delete key press
    def deleteKeyPressed(self):
        print "asdf"
        # If there is a selected point, and we're not in extend mode, delete it
        if (not self.extend_mode) and (not self.selected_index == None):
            self.removePoint(self.selected_index)
            self.selected_index = None


    def removePoint(self, index):
        self.num_points -= 1
        self.data_dict['x'] = np.delete(self.data_dict['x'], index)
        self.data_dict['y'] = np.delete(self.data_dict['y'], index)
        self.data_dict['symbolPen'].pop(index)
        self.data_dict['data'] = range(self.num_points)
        self.updateData()


    def updateData(self):
        pg.PlotDataItem.setData(self, **self.data_dict)


    def shape(self):
        # Inherit shape from the curve item
        return self.scatter.shape()

    def boundingRect(self):
        # All graphics items require this method (unless they have no contents)
        return self.shape().boundingRect()

    def paint(self, p, *args):
        # All graphics items require this method (unless they have no contents)
        return








g = CustomDataItem()
data_xs = np.array([0., 0.1, 0.5])
data_ys = np.array([0., 0.5, 0.])
g.setData(x = data_xs, y = data_ys, symbolSize = 25., pxMode = True)
v.addItem(g)

key_pressed = {'e' : False}
key_pressed = {'del' : False}

# Mouse click event
def mouse_click(e):
    g.offPointClick()

# Key press event
def key_press(e):
    if e.key() == 16777223:
        key_pressed['del'] = True
        g.deleteKeyPressed()
    if e.key() == 69:
        key_pressed['e'] = True
        g.extendKeyPressed()



# Key release
def key_release(e):
    if e.key() == 69:
        key_pressed['e'] = False

# Mouse move
def mouse_move(ev):
    if not ev.isExit():
        x = v.mapSceneToView(ev.pos()).x()
        y = v.mapSceneToView(ev.pos()).y()
        print x, y
        g.mouseMove(x, y)

v.mouseClickEvent = mouse_click
w.keyboardGrabber()
w.keyPressEvent = key_press
w.keyReleaseEvent = key_release
v.hoverEvent = mouse_move



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
