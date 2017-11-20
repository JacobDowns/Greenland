
import numpy as np
from scipy.integrate import ode
from scipy import interpolate
from scipy import optimize
from matplotlib import pyplot as plt

"""
Integrates along flow line.
"""

class WidthCalculator():

    def __init__(self, c_ts, c_x_interp, c_y_interp, b_x_interp, b_y_interp):

        # Times associates with c_xs and c_ys
        self.c_ts = c_ts
        # Center interpolated curves
        self.c_x_interp = c_x_interp
        self.c_y_interp = c_y_interp
        # Boundary flow line interpolated curves
        self.b_x_interp = b_x_interp
        self.b_y_interp = b_y_interp

        self.tan = np.array([0., 0.])
        self.x0 = 0.
        self.y0 = 0.


    # Set the currently displayed data field
    def calc_width(self):
        i = 0
        # Delta t used to compute tangent to center curve
        dt = 1e-6
        # Optimization parameter
        t_opt = 0.0

        ts = np.linspace(0., 1., 1500)
        b_xs = self.b_x_interp(ts)
        b_ys = self.b_y_interp(ts)
        c_xs = self.c_x_interp(ts)
        c_ys = self.c_y_interp(ts)

        plt.plot(b_xs, b_ys, 'b')
        plt.plot(c_xs, c_ys, 'k')

        # roots correspond to line intersections
        def f(t):
            # u and v coordinates of boundary curve where origin is centered at x0, y0
            u = self.b_x_interp(t) - self.x0
            v = self.b_y_interp(t) - self.y0
            print self.tan
            # Return component of (u,v) in direction of tangent
            return np.dot(np.array([u,v]), self.tan)

        # Compute tangent lines to curve at even intervals and find intersections
        # with boundary curve

        print self.c_ts

        for c_t in self.c_ts:
            # Select a point on the curve
            self.x0 = self.c_x_interp(c_t)
            self.y0 = self.c_y_interp(c_t)

            # Compute tangent to curve
            tx = (self.c_x_interp(c_t + dt) - self.x0) / dt
            ty = (self.c_y_interp(c_t + dt) - self.y0) / dt
            self.tan[0] = tx
            self.tan[1] = ty # = np.array([tx, ty])

            #plt.plot(ts, np.array(map(f, ts)))
            #plt.show()

            # Try to find an intersection of the normal at the point and the boundary
            # curve
            try :
                t_opt = optimize.brentq(f, 0., 1.0, xtol = 1e-7)
                print "t_opt", t_opt
                print "f", t_opt
                plt.plot([self.x0, self.b_x_interp(t_opt)], [self.y0, self.b_y_interp(t_opt)], 'ro-', ms = 5)

            except:
                # Catches exception that f must have opposite signs at ends of interval
                print "fail"
                pass

        plt.axes().set_aspect('equal', 'datalim')
        plt.show()
            #plt.plot([x0, x0 + scale*nx], [y0, y0 + scale*ny], 'ro-')



        #quit()
