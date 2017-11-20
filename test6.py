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
        # Index of point being dragged
        self.drag_index = None
        # How far to translate dragged point from original position
        self.drag_offset = None
        # Pen for highlighted pint
        self.selected_pen = pg.mkPen(pg.mkColor('r'))
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

        pg.GraphItem.__init__(self)


        ### Event handling
        # Triggered when a point is clicked
        self.scatter.sigClicked.connect(self.pointClicked)


    ### Sets the initial data
    def setData(self, **kwds):
        self.data = kwds

        # We need two fields in
        # Check to make sure we got all required fields
        cond1 = 'xc' in kwds and 'yc' in kwds
        cond2 = 'xb1' in kwds and 'yb1' in kwds
        cond3 = 'xb2' in kwds and 'yb2' in kwds

        if cond1 and cond2 and cond3:

            # Points on center flowline
            xs = self.data.pop('xc')
            ys = self.data.pop('yc')
            # Points on boundary flowlines
            xb1 = self.data.pop('xb1')
            yb1 = self.data.pop('yb1')
            xb2 = self.data.pop('xb2')
            yb2 = self.data.pop('yb2')

            # Number of points along center flowline
            self.num_center_points = len(xs)


            ### Position data for graph

            pos_xs = np.zeros(3 * self.num_center_points)
            pos_ys = np.zeros(3 * self.num_center_points)

            pos_xs[0::3] = xs
            pos_ys[0::3] = ys
            pos_xs[1::3] = xb1
            pos_ys[1::3] = yb1
            pos_xs[2::3] = xb2
            pos_ys[2::3] = yb2

            pos = np.array([pos_xs, pos_ys]).transpose()
            self.data['pos'] = pos

            ### Refresh adjacency and point data
            self.setAdjacency()
            self.setPointData()
            self.setSymbolPens()


            ### Define symbol pens

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

            # Get the index of the dragged point
            self.drag_index = pts[0].data()['index']
            # Offset from the original position
            self.drag_offset = self.data['pos'][self.drag_index] - pos
            # Select this point
            self.deselectAll()
            self.addSelectedPoint(self.drag_index)

        elif ev.isFinish():
            self.drag_index = None
            return
        else:
            if self.drag_index is None:
                ev.ignore()
                return

        ### In the midst of a drag

        #self.data['pos'][self.drag_index] = ev.pos() + self.drag_offset
        self.setPointCoords(self.drag_index, ev.pos() + self.drag_offset)
        self.updateGraph()
        ev.accept()


    ### Sets coordinates of point with given index
    def setPointCoords(self, index, coords):
        print "coords", coords
        self.data['pos'][index] = coords


    ### Insert a point. Takes an index from 0 to self.num_center_points
    def insertPoint(self, index, c_pos, b1_pos, b2_pos):
        index = 3*index
        self.num_center_points += 1

        # Insert position data
        pos_block = np.array([c_pos, b1_pos, b2_pos])
        self.data['pos'] = np.insert(self.data['pos'], index, pos_block, axis = 0)

        # Update adjacency data
        adj_block = np.array([[0,1], [0,2], [-3, 0]]) + (self.num_center_points - 1)*3
        self.data['adj'] = np.append(self.data['adj'], adj_block, axis = 0)

        # Update point data
        last_c_index = (self.num_center_points-1)*3
        data_block = np.array([(last_c_index, 'c'), (last_c_index + 1, 'b'),
            (last_c_index + 2, 'b')], dtype = self.data['data'].dtype)
        self.data['data'] = np.append(self.data['data'], data_block)

        # Update symbol pens
        self.data['symbolPen'] = np.append(self.data['symbolPen'], np.array([self.default_pen, self.default_pen, self.default_pen]))

        self.updateGraph()


    ### Adds a point at beginning of path
    def addPointStart(self, x, y):
        pass


    ### Adds a point at end of path
    def addPointEnd(self, x, y):
        self.num_points += 1
        self.data_dict['x'] = np.append(self.data_dict['x'], x)
        self.data_dict['y'] = np.append(self.data_dict['y'], y)
        self.data_dict['data'] = range(self.num_points)
        self.data_dict['symbolPen'].append(self.default_pen)


    ### Remove points with given indexes
    def removePoints(self, indexes):

        self.num_center_points -= len(indexes)
        # Modify position data
        delete_indexes = np.concatenate([indexes, indexes + 1, indexes +2])
        self.data['pos'] = np.delete(self.data['pos'], delete_indexes, axis = 0)
        # Reset the adjacency and point data, which is now messed up
        self.setAdjacency()
        self.setPointData()
        self.setSymbolPens()

        self.updateGraph()


    ### Set adjacency data after points have been inserted or removed
    def setAdjacency(self):
        center_indexes = np.arange(0, 3*self.num_center_points, 3)
        from_indexes = np.concatenate([center_indexes, center_indexes, center_indexes[1:]])
        to_indexes = np.concatenate([center_indexes + 1, center_indexes + 2, center_indexes[:-1]])
        adj = np.array([from_indexes, to_indexes]).transpose()
        self.data['adj'] = adj


    ### Sets point data after points have been inserted or removed
    def setPointData(self):
        # Point indexes
        self.data['data'] = np.empty((3*self.num_center_points,),  dtype=[('index', '>i4'),('type', '|S10')])
        self.data['data']['index'][:] = np.arange(3*self.num_center_points)
        # Point types
        point_types = np.empty(3 * self.num_center_points, dtype = '|S10')
        point_types[0::3] = 'c'
        point_types[1::3] = 'b'
        point_types[2::3] = 'b'

        self.data['data']['type'][:] = point_types


    ### Sets symbol pens after points have been inserted or removed
    def setSymbolPens(self):
        pens = np.empty(3*self.num_center_points, dtype=object)
        pens[:] = self.default_pen
        self.data['symbolPen'] = pens


    ### Indicates a point is selected by usnig a different pen
    def addSelectedPoint(self, index):
        # Only select center points
        if self.data['data'][index][1] == 'c':
            self.selected_indexes.add(index)
            self.data['symbolPen'][index] = self.selected_pen


    ### Deselect all currently selected point
    def deselectAll(self):
        print "deselect", self.selected_indexes
        for index in self.selected_indexes:
            self.data['symbolPen'][index] = self.default_pen
        self.selected_indexes.clear()


    ### Dumb setter function for extend mode so I can keep track of when
    ### extend mode is toggled
    def setExtendMode(self, mode):
        self.extend_mode = mode
        print "extend mode", self.extend_mode


    ### Respond to a click that's not on a point
    def offPointClick(self):
        self.setExtendMode(False)
        self.deselectAll()
        self.updateGraph()


    ### Point click event: highlight the clicked point
    def pointClicked(self, p, pts):
        print "sf"
        if self.extend_mode:
            """
            self.deselectAll()
            if self.moving_point_index == 0:
                self.addPointStart(*self.getPointCoords(self.moving_point_index))
            else :
                self.addPointEnd(*self.getPointCoords(self.moving_point_index))
                self.moving_point_index += 1"""
        else :
            if not self.ctrl_pressed:
                self.deselectAll()
            print "sdf"
            self.addSelectedPoint(pts[0].data()['index'])

        self.updateGraph()


    ### Respond to delete key press
    def deleteKeyPressed(self):
        # If there is a selected point, and we're not in extend mode, delete it
        if (not self.extend_mode) and (not len(self.selected_indexes) == 0):
            self.removePoints(np.array(list(self.selected_indexes)))
            self.updateGraph()


    ### Triggers when e key is pressed for extend mode
    def extendKeyPressed(self):

        # Conditional to check if there's one selected point and it's either
        # the first or last node
        one_selected = len(self.selected_indexes) == 1
        first_selected = 0 in self.selected_indexes
        last_selected = (self.num_center_points - 1)*3 in self.selected_indexes
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

            #self.updateData()

        else :
            print "dasdf"
            self.setExtendMode(False)
            self.deselectAll()

        self.updateGraph()


    def updateGraph(self):
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
g.insertPoint(0, np.array([-0.75, 0.]), np.array([-0.75, 0.5]), np.array([-0.75, -0.5]))
g.insertPoint(0, np.array([-0.9, 0.]), np.array([-0.9, 0.5]), np.array([-0.9, -0.5]))
g.insertPoint(5, np.array([0.9, 0.]), np.array([0.9, 0.5]), np.array([0.9, -0.5]))

key_pressed = {}

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

# Mouse move
def mouse_move(ev):
    if not ev.isExit():
        x = v.mapSceneToView(ev.pos()).x()
        y = v.mapSceneToView(ev.pos()).y()
        #g.mouseMove(x, y)

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
