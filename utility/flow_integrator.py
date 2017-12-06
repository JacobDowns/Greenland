
import numpy as np
from scipy.integrate import ode
from scipy import interpolate
from scipy import optimize

"""
Integrates along flow line.
"""

class FlowIntegrator():

    def __init__(self, data_loader):

        self.data_loader = data_loader

        # Velocity right hand side function
        def rhs(t, u):
            x = u[0]
            y = u[1]
            d = u[2]

            vx = data_loader.get_field_val('VX', x, y)
            vy = data_loader.get_field_val('VY', x, y)
            v_mag = np.sqrt(vx**2 + vy**2)
            return np.array([-vx / v_mag, -vy / v_mag, v_mag])

        # ODE integrator
        self.integrator = ode(rhs).set_integrator('vode', method = 'adams')


    # Set the currently displayed data field
    def integrate(self, x0, y0):
        u0 = np.array([x0, y0, 0.])
        self.integrator.set_initial_value(u0, 0.0)

        # Approximate spacing in m between points (depends on actual flow path)
        spacing = 1000.0
        dist_mult = 150.
        # time step
        dt = spacing / dist_mult

        # vx and vy at current location
        vx = self.data_loader.get_field_val('VX', x0, y0)
        vy = self.data_loader.get_field_val('VY', x0, y0)
        v_mag = np.sqrt(vx**2 + vy**2)

        # x and y positions along flow line
        xs = [x0]
        ys = [y0]
        # Distance traveled
        ds = [0.0]
        # times
        ts = [0.]

        i = 0
        while self.integrator.successful() and v_mag > 10.0:
            # Step forward
            u = self.integrator.integrate(self.integrator.t + dt)

            # Update v mag to check stopping condition
            x = u[0]
            y = u[1]
            d = u[2]
            xs.append(x)
            ys.append(y)
            ds.append(d)
            ts.append(self.integrator.t)

            vx = self.data_loader.get_field_val('VX', x, y)
            vy = self.data_loader.get_field_val('VY', x, y)
            v_mag = np.sqrt(vx**2 + vy**2)

        """
        # Last point along the curve
        x_last = x0
        y_last = y0

        # Desired spacing between points on curve
        spacing = 15.0

        # Distance from point on curve at time t to last point
        def f(t):
            return (np.sqrt( (x_interp(t) - x_last)**2 + (y_interp(t) - y_last)**2) - spacing)

        t0 = 0.
        sample_ts = []
        try :
            while t0 <= 1.0:
                t0 = optimize.brentq(f, float(t0), 1.0, xtol = 1e-5)
                x_last = x_interp(t0)
                y_last = y_interp(t0)
                xs_spaced.append(x_last)
                ys_spaced.append(y_last)
                sample_ts.append(t0)
        except:
            # Catches exception that f must have opposite signs at ends of interval
            pass"""


        return np.array(xs), np.array(ys), np.array(ts)
