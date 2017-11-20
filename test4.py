import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import copy

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
        # Index of point being dragged
        self.drag_point_index = None
        # How much to translate that point by
        self.drag_offset = None
        # Pen for highlighted pint
        self.highlight_pen = pg.mkPen(pg.mkColor('r'))
        # Pen for default points
        self.default_pen = default_pen = pg.mkPen(pg.mkColor('w'))
        # Number of points
        self.num_points = 0
        # Index of selected point
        self.selected_indexes = set([])
        # Extend mode?
        self.extend_mode = False
        # Moving point
        self.moving_point_index = None
        # Control button pressed
        self.ctrl_pressed = False

        pg.PlotDataItem.__init__(self)

        ### Event handling

        # Triggered when a point is clicked
        self.scatter.sigClicked.connect(self.pointClicked)


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
        self.data_dict['symbolPen'].insert(0, self.default_pen)



    ### Adds a point at end of path
    def addPointEnd(self, x, y):
        self.num_points += 1
        self.data_dict['x'] = np.append(self.data_dict['x'], x)
        self.data_dict['y'] = np.append(self.data_dict['y'], y)
        self.data_dict['data'] = range(self.num_points)
        self.data_dict['symbolPen'].append(self.default_pen)


    ### Insert a point at index
    def insertPoint(self, index):
        self.deselectAll()
        self.num_points += 1
        x0, y0 = self.getPointCoords(index)
        x1, y1 = self.getPointCoords(index + 1)
        xp = (x0 + x1) / 2.
        yp = (y0 + y1) / 2.
        self.data_dict['x'] = np.insert(self.data_dict['x'], index+1, xp)
        self.data_dict['y'] = np.insert(self.data_dict['y'], index+1, yp)
        self.data_dict['symbolPen'].insert(index+1, self.default_pen)
        self.data_dict['data'] = range(self.num_points)



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


    ### Indicates a point is selected by usnig a different pen
    def addSelectedPoint(self, index):
        self.selected_indexes.add(index)
        self.data_dict['symbolPen'][index] = self.highlight_pen


    ### Deselect all currently selected point
    def deselectAll(self):
        print "deselect", self.selected_indexes
        for index in self.selected_indexes:
            self.data_dict['symbolPen'][index] = self.default_pen
        self.selected_indexes.clear()


    ### Deselect a point by giving it the default pen
    def removeSelectedPoint(self, index):
        if index in self.selected_indexes:
            self.selected_indexes.remove(index)


    ### Triggers when e key is pressed for extend mode
    def extendKeyPressed(self):

        # Conditional to check if there's one selected point and it's either
        # the first or last node
        one_selected = len(self.selected_indexes) == 1
        first_selected = 0 in self.selected_indexes
        last_selected = self.num_points - 1 in self.selected_indexes
        cond = one_selected and (last_selected or first_selected)

        if (not self.extend_mode) and cond:
            # Enable extend mode
            self.setExtendMode(True)

            # If selected point is at beginning of path, add point starting from
            # there. If selected point is at end, start it from there.
            self.deselectAll()
            if first_selected:
                self.addPointStart(*self.getPointCoords(0))
                self.moving_point_index = 0
            else :
                self.addPointEnd(*self.getPointCoords(self.num_points - 1))
                self.moving_point_index = self.num_points - 1

            self.updateData()

        else :
            print "dasdf"
            self.setExtendMode(False)
            self.deselectAll()


    ### Dumb setter function for extend mode
    def setExtendMode(self, mode):
        self.extend_mode = mode
        print "extend mode", self.extend_mode


    ### Respond to an off point click event
    def offPointClick(self):
        self.setExtendMode(False)
        self.deselectAll()
        self.updateData()


    ### Point click event: highlight the clicked point
    def pointClicked(self, p, pts):
        if self.extend_mode:
            self.deselectAll()
            if self.moving_point_index == 0:
                self.addPointStart(*self.getPointCoords(self.moving_point_index))
            else :
                self.addPointEnd(*self.getPointCoords(self.moving_point_index))
                self.moving_point_index += 1
        else :
            if not self.ctrl_pressed:
                self.deselectAll()
            self.addSelectedPoint(pts[0].data())

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
        # If there is a selected point, and we're not in extend mode, delete it
        if (not self.extend_mode) and (not len(self.selected_indexes) == 0):
            self.removePoints(list(self.selected_indexes))
            self.updateData()


    ### Respond to s key pressed
    def sKeyPressed(self):
        # If we're not in extend mode, check if there are two adjacent vertices
        # selected
        if not self.extend_mode and len(self.selected_indexes) == 2:
            indexes = list(self.selected_indexes)
            if abs(indexes[0] - indexes[1]) == 1:
                self.insertPoint(min(indexes[0], indexes[1]))
                self.updateData()




    ### Remove points at indexes
    def removePoints(self, indexes):
        self.num_points -= len(indexes)
        self.data_dict['x'] = np.delete(self.data_dict['x'], indexes)
        self.data_dict['y'] = np.delete(self.data_dict['y'], indexes)
        self.data_dict['symbolPen'] = list(np.delete(np.array(self.data_dict['symbolPen']), indexes))
        self.selected_indexes = self.selected_indexes.difference(set(indexes))
        self.data_dict['data'] = range(self.num_points)



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
    if e.key() == 83:
        g.sKeyPressed()
    if e.key() == 16777249:
        g.ctrl_pressed = True
    if e.key() == 16777223:
        key_pressed['del'] = True
        g.deleteKeyPressed()
    if e.key() == 69:
        key_pressed['e'] = True
        g.extendKeyPressed()



# Key release
def key_release(e):
    if e.key() == 16777249:
        g.ctrl_pressed = False
    if e.key() == 69:
        key_pressed['e'] = False

# Mouse move
def mouse_move(ev):
    if not ev.isExit():
        x = v.mapSceneToView(ev.pos()).x()
        y = v.mapSceneToView(ev.pos()).y()
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
