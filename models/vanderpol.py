import sympy as sp
import numpy as np

from kaa.bundle import Bundle
from kaa.model import Model


class VanDerPol(Model):

    def __init__(self, delta=0.02):

        x, y = sp.Symbol('x'), sp.Symbol('y')
        dx = x + y*delta
        dy = y + (1*(1-x**2)*y - 2*x + x)*delta

        vars = [x,y]
        dyns = [dx, dy]

        dim_sys = 2
        num_dirs = 4
        num_temps = 6

        L = np.zeros([num_dirs, dim_sys])

        L[0][0] = 1
        L[1][1] = 1
        L[2][0] = -1; L[2][1] = 1;
        L[3][0] = 1; L[3][1] = 1;

        T = np.zeros([num_temps, dim_sys])
        T[0][0] = 0; T[0][1] = 1;
        T[1][0] = 0; T[1][1] = 2;
        T[2][0] = 0; T[2][1] = 3;
        T[3][0] = 1; T[3][1] = 2;
        T[4][0] = 1; T[4][1] = 3;
        T[5][0] = 2; T[5][1] = 3;


        offu = np.zeros(num_dirs);
        offl = np.zeros(num_dirs);

        offu[0] = 0.03; offl[0] = 0;
        offu[1] = 2; offl[1] = -1.94;
        offu[2] = 10; offl[2] = 10;
        offu[3] = 10; offl[3] = 10;

        super().__init__(dyns, vars, T, L, offu, offl, "VDP")

class VanDerPol_UnitBox(Model):

    def __init__(self, delta=0.02):

        x, y = sp.Symbol('x'), sp.Symbol('y')
        dx = x + y*delta
        dy = y + (1*(1-x**2)*y - 2*x + x)*delta

        vars = [x,y]
        dyns = [dx, dy]

        dim_sys = 2
        num_dirs = 2
        num_temps = 1

        L = np.zeros([num_dirs, dim_sys])

        L[0][0] = 1
        L[1][1] = 1

        T = np.zeros([num_temps, dim_sys])
        T[0][0] = 0; T[0][1] = 1;

        offu = np.zeros(num_dirs);
        offl = np.zeros(num_dirs);

        offu[0] = 0.03; offl[0] = 0;
        offu[1] = 2; offl[1] = -1.94;

        super().__init__(dyns, vars, T, L, offu, offl, name="VDP")
