from math_functions import *
from pens import *
from gui import *
from dataset_objects import *
import numpy as np
from data_functions import *
from scipy.integrate import ode
from classes.pltPoints import *
from velocity_functions import *

def centerVelocityStream(x, y):
    x0p, y0p = projCoord(x, y)
    y0 = np.array([x0p, y0p])
    t0, t1, dt = 0, 80, .1
    r = ode(getProfile).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t0)
    ox = []
    oy = []
    ind = 0
    while r.successful() and ind < 2:
        '''
        what the fuck was I trying to do here??
        I think, integrate then look perpindicular for the velocity width margins
        '''
        ai = r.integrate(r.t + dt)
        ind += 1
        xi, yi = mapCoord(np.real(ai[0]), np.real(ai[1]))
        ox.append(xi)
        oy.append(yi)
    iiContainer.currentWidget().addItem(pg.PlotDataItem(ox, oy, pen=plotPen3))

    endPoints = [[0, 0], [0, 0]] # either side of the velocity stream
    endPoints[0][0], endPoints[0][1], endPoints[1][0], endPoints[1][1] = calcVelWidth(x, y, ox[-1], oy[-1], False)
    d = (0.5) * sqrt((endPoints[0][0] - endPoints[1][0]) ** 2 + (endPoints[0][1] - endPoints[1][1]) ** 2)
    theta = np.arctan2(float(y - oy[-1]), float(x - ox[-1]))
    x, y = endPoints[0][0] + (d * -np.sin(theta)), endPoints[0][1] + (d * np.cos(theta))
    return x, y

def mouseClick(e):
    global vptSel, vptCur, integrateLine, shift
    first = False
    if len(vpts) == 0:
        first = True
        x = e.pos().x()
        y = e.pos().y()
        if autoCorrectVpt.checkState() == 2:
            x, y = centerVelocityStream(x, y)

    print 'shift: ', shift
    if shift:
        intLine(e)
    else:
        if not vptSel:
            for pt in vpts:
                if pt.checkClicked(e.pos()):
                    vptSel = True
                    vptCur = pt
            if not vptSel:
                if not first:
                    x = e.pos().x()
                    y = e.pos().y()
                px, py = projCoord(x,y)
                vxInterp, vyInterp = getInterpolators(velocity.vx, 'vxvy', x, y, d2=velocity.vy)
                surfaceInterp = getInterpolators(surface.data, surface.name, x, y)
                vxd = vxInterp([px], [py], grid=False)
                vyd = vyInterp([px], [py], grid=False)
                sur = surfaceInterp([px], [py], grid=False)
                v0 = sqrt(vxd**2 + vyd**2)
                vpts.append(vpt(x, y, v0, velocity.plotWidget)) # in map coordinates x<10018, y< 17946
                x = int(np.floor(x))
                y = int(np.floor(y))
                txt = 'Point ' + str(len(vpts)-1) + \
                ':\n=================\n' + \
                'x: ' + str(x) + '\n' +\
                'y: ' + str(y) + '\n' +\
                'v: ' +      "{:.3f}".format(velocity.data[y][x]) + \
                '\nbed: ' +  "{:.3f}".format(bed.data[y][x]) + \
                '\nsurf: ' + "{:.3f}".format(surface.data[y][x]) + \
                '\nSMB: ' +  "{:.3f}".format(smb.data[y][x]*(1.0/1000.0)*(916.7/1000.0)) + \
                '\nSMB: ' +  "{:.3f}".format(smb.data[y][x]) + '\n\n'

                textOut.append(txt)
                iiContainer.currentWidget().addItem(vpts[-1].getCross()[0])
                iiContainer.currentWidget().addItem(vpts[-1].getCross()[1])
                if len(vpts) > 1:
                    xa = [vpts[-1].getX(), vpts[-2].getX()]
                    ya = [vpts[-1].getY(), vpts[-2].getY()]
                    vpts[-2].setLine(pg.PlotDataItem(xa,ya,connect='all'))
                    iiContainer.currentWidget().addItem(vpts[-2].getLine())#,pen=plotPen)
        else:
            vptSel = False



def calcProf(e):
    global integrateLine
    x0p, y0p = projCoord(vpts[-1].getX(), vpts[-1].getY())
    y0 = np.array([x0p, y0p])
    t0, t1, dt = 0, 80, .1
    r = ode(getProfile).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t0)
    print "Printing integration points"
    ox = [vpts[-1].getX()]
    oy = [vpts[-1].getY()]
    while r.successful() and r.t < t1:
        # print(r.t+dt, r.integrate(r.t+dt))
        ai = r.integrate(r.t+dt)
        xi, yi = mapCoord(ai[0], ai[1])
        # print 'xi, iy: ', xi, yi
        ox.append(np.real(xi))
        oy.append(np.real(yi))

    # print 'ox, oy: ', ox, oy
    integrateLine = pg.PlotDataItem(ox,oy,pen=plotPen2)
    iiContainer.currentWidget().addItem(integrateLine)


def changeMap(index):
    '''
    Called when data-set drop down menu is changed.
    :param index:
    :return:
    '''

    # print iiContainer.currentWidget()
    vr = iiContainer.currentWidget().getPlotItem().getViewBox().viewRange()

    print 'range: ', vr
    # print '       ', oldthick.plotWidget.getPlotItem().getViewBox().state['limits']['xLimits']
    global currentMap
    if index == 0 and currentMap != 0:
        #velocity
        currentMap = 0
        iiContainer.setCurrentWidget(velocity.plotWidget)
        velocity.imageItem.mouseClickEvent = mouseClick
        velocity.plotWidget.getPlotItem().getViewBox().setRange(xRange=vr[0], yRange=vr[1], padding=0.0)
    elif index == 1 and currentMap != 1:
        #bed
        currentMap = 1
        iiContainer.setCurrentWidget(bed.plotWidget)
        bed.imageItem.mouseClickEvent = mouseClick
        bed.plotWidget.getPlotItem().getViewBox().setRange(xRange=vr[0], yRange=vr[1], padding=0.0)
    elif index == 2 and currentMap != 2:
        #surface
        currentMap = 2
        iiContainer.setCurrentWidget(surface.plotWidget)
        surface.plotWidget.getPlotItem().getViewBox().setRange(xRange=vr[0], yRange=vr[1], padding=0.0)
    elif index == 3 and currentMap != 3:
        #SMB
        currentMap = 3
        iiContainer.setCurrentWidget(smb.plotWidget)
        smb.plotWidget.getPlotItem().getViewBox().setRange(xRange=vr[0], yRange=vr[1], padding=0.0)
    elif index == 4 and currentMap != 4:
        #THICKNESS
        currentMap = 4
        iiContainer.setCurrentWidget(thickness.plotWidget)
        thickness.plotWidget.getPlotItem().getViewBox().setRange(xRange=vr[0], yRange=vr[1], padding=0.0)


def calcBP():
    '''
    Calculate the data for bottom plot then populate the plot.
    :return:
    '''
    global dr, bpLegend, dataLen, botPlot
    # Empty the graph
    velocity.pathPlotItem.clear()
    surface.pathPlotItem.clear()
    smb.pathPlotItem.clear()
    bed.pathPlotItem.clear()
    velocityWidth.pathPlotItem.clear()
    thickness.pathPlotItem.clear()
    if len(vpts) > 0:
        print 'Plotting...'
        # nbed, nsurf, nv, nsmb, nvelWidth, linePoints, graphX = interpolateData(True)
        interpolateData(True)
        if velocityCheck.checkState() == 2:
            velocity.pathPlotItem.setData(velocity.distanceData          , velocity.pathData)
        if smbCheck.checkState() == 2:
            smb.pathPlotItem.setData(smb.distanceData                    , smb.pathData)
        if vWidthCheck.checkState() == 2:
            velocityWidth.pathPlotItem.setData(velocityWidth.distanceData, velocityWidth.pathData)
        if surfaceCheck.checkState() == 2:
            surface.pathPlotItem.setData(surface.distanceData            , surface.pathData)
        if bedCheck.checkState() == 2:
            bed.pathPlotItem.setData(bed.distanceData                    , bed.pathData)
        thickness.pathPlotItem.setData(thickness.distanceData, thickness.pathData)
        velocityWidth.pathPlotItem.setData(velocityWidth.distanceData, velocityWidth.pathData)
        pg.QtGui.QApplication.processEvents()
        print 'Done plotting'

def mouseMoved(e):
    global vptSel, vptCur, integrateLine, currentMap
    if e.isExit() is False:
        if vptSel and integrateLine is not None:
            cData = integrateLine.curve.getData()
            imin = curveDistance(e.pos().x(), e.pos().y(), cData)
            if imin != -1:
                x = cData[0][imin]
                y = cData[1][imin]
                vptCur.updateCross(x,y)
            else:
                vptCur.updateCross(e.pos().x(), e.pos().y())
        # else:
        x = int(np.floor(e.pos().x()))
        y = int(np.floor(e.pos().y()))
        if np.abs(x) <= 10018 and np.abs(y) <= 17946:
            mouseCoordinates.setText('x: ' + str(x) + '\ty: ' + str(y) + '\n' + 'th: ' + str(thickness.data[y][x]))# + '\n' + 'oth: ' + str(oldthick.data[y][x]))
            # if currentMap == 0:
                # Interpolating every spot is too much, causes lag
                # vInt = getInterpolators(sqrt(velocity.vx**2 + velocity.vy**2), 'v', x,y)
                # px, py = projCoord(x,y)
                # vLocal = vInt([px],[py], grid=False)
                # t = 'v: ' + str(velocity.data[y][x]) + '\tbed: ' + str(bed.data[y][x]) + '\tsurf: ' + str(surface.data[y][x]) + '\tSMB: ' + str(smb.data[y][x])
                # t = t + '\t bed: ' + str(bed[int(np.ceil(np.abs(y)))][int(np.floor(np.abs(x)))])  + '\t surface: ' + str(surfaceVals[int(np.ceil(np.abs(y)))][int(np.floor(np.abs(x)))])
                # mouseCoordinates.setText(t)

            # elif currentMap == 1:
            #     # print 'mm 31'
            #     mouseCoordinates.setText('x: ' + str(x) + '\ty: ' + str(y) + '\t bed: ' + str(bed.data[int(np.ceil(np.abs(y)))][int(np.floor(np.abs(x)))]))
            # elif currentMap == 2:
            #     # print 'mm 32'
            #     mouseCoordinates.setText('x: ' + str(x) + '\ty: ' + str(y) + '\t surface: ' + str(surface.data[int(np.ceil(np.abs(y)))][int(np.floor(np.abs(x)))]))


def mouseMovedBP(evt):
    global bpLegend, dataLen
    print 'mouse moved bottom plot'
    if botPlot:
        print 'is not not not none'
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if bp.getPlotItem().sceneBoundingRect().contains(pos):
            mousePoint = bp.getPlotItem().vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(velocity.pathData):
                velocity.legendItem.setText('Velocity' + str(velocity.pathData[index]))
                smb.legendItem.setText('SMB ' + str(smb.pathData[index]))
                velocityWidth.legendItem.setText('Velocity Width ' + str(velocityWidth.pathData[index]))
                surface.legendItem.setTxt('Surface ele ' + str(surface.pathData[index]))
    # else:
        # print 'It is NONE'


def arrows():
    ''''
    Plot velocity vectors to see the velocity field and its borders
    '''
    print 'arrows'
    print velocity.imageItem.getViewBox().viewRange() # [y0, y1] [x0, x1]
    rngx, rngy = velocity.imageItem.getViewBox().viewRange()
    print rngx
    print rngy
    print 'Starting arrows'
    for i in range(int(rngx[0]),int(rngx[1])):
        for j in range(int(rngy[0]), int(rngy[1])):
            vdir = [velocity.vx[j][i], -velocity.vy[j][i]]
            vmag = sqrt(velocity.vx[j][i]**2 +  velocity.vy[j][i]**2)
            # theta = np.arctan2(vdir[1], vdir[0])
            iiContainer.currentWidget().addItem(pg.PlotDataItem([(i+0.5),(i+0.5 + vdir[0]/(1.5*vmag))], [(j+0.5),(j+0.5 + vdir[1]/(1.5*vmag))], pen=plotPen2))
            iiContainer.currentWidget().addItem(pg.PlotDataItem([i+0.5], [j+0.5]), pen=(255,255,255), symbolBrush=(255,0,0), symbolPen='w')
    print 'finished arrows'


def calcProf(e):
    '''
    Calculates the line that shows velocity flow inwards (negative direction).
    :param e:
    :return:
    '''
    global integrateLine
    x0p, y0p = projCoord(vpts[-1].getX(), vpts[-1].getY())
    y0 = np.array([x0p, y0p])
    t0, t1, dt = 0, 80, .1
    r = ode(getProfile).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t0)
    print "Printing integration points"
    ox = [vpts[-1].getX()]
    oy = [vpts[-1].getY()]
    while r.successful() and r.t < t1:
        # print(r.t+dt, r.integrate(r.t+dt))
        ai = r.integrate(r.t+dt)
        xi, yi = mapCoord(ai[0], ai[1])
        # print 'xi, iy: ', xi, yi
        ox.append(np.real(xi))
        oy.append(np.real(yi))

    print 'ox, oy: ', ox, oy
    integrateLine = pg.PlotDataItem(ox,oy,pen=plotPen2)
    iiContainer.currentWidget().addItem(integrateLine)



def regionIntLine(e):
    '''
    Calculates and prints the integrated velocity path for several paths in a velocity stream.
    :param e:
    :return:
    '''
    xp0 = vpts[-1].getX()
    yp0 = vpts[-1].getY()
    xp1 = vpts[-2].getX()
    yp1 = vpts[-2].getY()
    xril, yril, xrir, yrir = calcVelWidth(xp0, yp0, xp1, yp1, False)  # for vpts[-1]

    theta = np.arctan2((yril - yrir), (xril - xrir))
    d = sqrt((yril - yrir) ** 2 + (xril - xrir) ** 2)
    dr = 10
    l = linspace(-d / 2, d / 2, dr, endpoint=True)

    rotMatrix = np.matrix([[np.cos(theta), -1 * np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    lines = []

    for i in range(len(l)):
        '''
            Moves along velocity width line. 
            Good spot for parallel programming.
        '''
        print l[i]
        trot = rotMatrix * np.matrix([[l[i]], [0.0]])
        x0p, y0p = projCoord((xp1 + trot[0, 0]), (yp1 + trot[1, 0]))
        lines.append(intLine(x0p, y0p))
        iiContainer.currentWidget().addItem(lines[-1])




def ky(e):
    global shift
    print 'key pressed ', e.key()
    print 'type: -' + str(e.type()) + '-'
    #6 is press, 7 is release
    if e.type() == 6:
        print 'shift true'
        shift = True
    else:
        shift = False
        print 'shift false'
    # 16777249 is shift
