
import numpy as np
from scipy.integrate import ode
from scipy.interpolate import interp1d
from scipy import optimize
from matplotlib import pyplot as plt
from utility.flowline_graph import *

"""
Calcululates ice stream with.
"""

class WidthCalculator():

    def __init__(self, xc, yc, xb1, yb1, xb2, yb2, resolution):

        ts1 = np.linspace(0., 1., len(xc))
        ts2 = np.linspace(0., 1., len(xb1))
        ts3 = np.linspace(0., 1., len(xb2))

        # Parameterized Center curve x(t), y(t) with 0 <= t <=1
        self.xc_interp = interp1d(ts1, xc)
        self.yc_interp = interp1d(ts1, yc)
        # Firstboundary  curve x(t), y(t) with 0 <= t <=1
        self.xb1_interp = interp1d(ts2, xb1)
        self.yb1_interp = interp1d(ts2, yb1)
        # Second boundary curve x(t), y(t) with 0 <= t <=1
        self.xb2_interp = interp1d(ts3, xb2)
        self.yb2_interp = interp1d(ts3, yb2)

        # Desired mesh resolution
        self.resolution = resolution
        # Caclulate evenly spaced points along the center line
        self.space_points()


    ### Find evenly spaced points along the center curve
    def space_points(self):
        # Previous point along the curve
        x_last = self.xc_interp(0.)
        y_last = self.yc_interp(0.)
        # Coordinates of evenly spaced points
        xs_spaced = [x_last]
        ys_spaced = [y_last]
        # Times at which spaced points occur
        ts_spaced = [0.]
        # Optimization parameter
        t_opt = 0.
        # Desired spacing between points on curve
        spacing = self.resolution / 150.

        # Distance from point on curve at time t to last point
        def f(t):
            return (np.sqrt( (self.xc_interp(t) - x_last)**2 + (self.yc_interp(t) - y_last)**2) - spacing)

        try :
            while t_opt <= 1.0:
                # Find a point that is distance spacing from the previous one
                t_opt = optimize.brentq(f, float(t_opt), 1.0, xtol = 1e-5)

                x_last = self.xc_interp(t_opt)
                y_last = self.yc_interp(t_opt)

                xs_spaced.append(x_last)
                ys_spaced.append(y_last)

                # This will be useful for computing normal vector at this point
                ts_spaced.append(t_opt)
        except:
            # Catches exception that f must have opposite signs at ends of interval
            pass

        xs_spaced.append(self.xc_interp(1.))
        ys_spaced.append(self.yc_interp(1.))

        self.xs_spaced = np.array(xs_spaced)
        self.ys_spaced = np.array(ys_spaced)
        self.ts_spaced = np.array(ts_spaced)


    ### Calculates width from centerline to boundary curve
    def calc_width(self, xb_interp, yb_interp):
        # Delta t used to compute tangent to center curve
        dt = 1e-6
        # Optimization parameter
        t_opt = 0.0
        # Tangent to center curve
        tan = np.array([0., 0.])
        # Current point on center curve
        x0 = 0.
        y0 = 0.
        # Coordinates of intersection points
        int_xs = np.zeros(len(self.xs_spaced))
        int_xs[:] = self.xs_spaced
        int_ys = np.zeros(len(self.xs_spaced))
        int_ys[:] = self.ys_spaced

        # roots correspond to intersections of boundary flow line with normal vector
        # at the current point on the central flow line

        def f(t):
            # u and v coordinates of boundary curve where origin is centered at x0, y0
            u = xb_interp(t) - x0
            v = yb_interp(t) - y0
            # Return component of (u,v) in direction of tangent
            return np.dot(np.array([u,v]), tan)

        # Compute tangent lines to curve at even intervals and find intersections
        i = 0
        for c_t in self.ts_spaced:
            # Select a point on the curve
            x0 = self.xc_interp(c_t)
            y0 = self.yc_interp(c_t)

            # Compute tangent to curve
            tx = (self.xc_interp(c_t + dt) - x0) / dt
            ty = (self.yc_interp(c_t + dt) - y0) / dt
            tan[0] = tx
            tan[1] = ty

            # Try to find an intersection of the normal at the point and the boundary
            # curve
            try :
                t_opt = optimize.brentq(f, 0., 1.0, xtol = 1e-7)
                int_xs[i] = xb_interp(t_opt)
                int_ys[i] = yb_interp(t_opt)
            except Exception as inst:
                pass


            i += 1

        return int_xs, int_ys


    ### Return np array of widths
    def get_width(self):
        xs1, ys1 = self.calc_width(self.xb1_interp, self.yb1_interp)
        xs2, ys2 = self.calc_width(self.xb2_interp, self.yb2_interp)

        fg = FlowlineGraph()
        fg.setData(xc=self.xs_spaced, yc=self.ys_spaced, xb1=xs1, yb1=ys1, xb2=xs2, yb2=ys2, size = 25., pxMode = True)
        return fg
