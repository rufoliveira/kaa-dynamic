import random as rand
import numpy as np
import multiprocessing as mp

from operator import mul
from functools import reduce
from itertools import product
from kaa.lputil import minLinProg, maxLinProg
from kaa.settings import KaaSettings
from kaa.trajectory import Traj, TrajCollection

class ChebyCenter:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class LinearSystem:

    def __init__(self, model, A, b):
        self.A = A
        self.b = b
        self.model = model
        self.vars = model.vars
        self.dim = model.dim

    """
    Computes and returns the Chebyshev center of parallelotope.
    @returns self.dim point marking the Chebyshev center.
    """
    @property
    def chebyshev_center(self):

        'Initialize objective function for Chebyshev intersection LP routine.'
        c = [0 for _ in range(self.dim + 1)]
        c[-1] = 1

        row_norm = np.reshape(np.linalg.norm(self.A, axis=1), (self.A.shape[0], 1))
        center_A = np.hstack((self.A, row_norm))

        center_pt = maxLinProg(c, center_A, self.b).x
        return ChebyCenter(center_pt[:-1], center_pt[-1])

    """
    Volume estimation of system by sampling points and taking ratio.
    @params samples: number of samples used to estimate volume
    @returns estimated volume of linear system
    """
    @property
    def volume(self):
        envelop_box = self.__calc_envelop_box()
        num_contained_points = 0
        num_samples = KaaSettings.VolumeSamples

        for _ in range(num_samples):
            point = self.__sample_box_point(envelop_box)

            if self.check_membership(point):
                num_contained_points += 1

        return (num_contained_points / num_samples) * self.__calc_box_volume(envelop_box)

    """
    Maxmize optimization function y over Ax \leq b
    @params y: linear function to optimize over
    @returns LinProgResult
    """
    def max_opt(self, y):
        assert len(y) == self.dim, "Linear optimization function must be of same dimension as system."
        return maxLinProg(y, self.A, self.b)

    """
    Minimize optimization function y over Ax \leq b
    @params y: linear function to optimize over
    @returns LinProgResult
    """
    def min_opt(self, y):
        assert len(y) == self.dim, "Linear optimization function must be of same dimension as system."
        return minLinProg(y,self.A, self.b)

    """
    Checks if point is indeed contained in Ax \leq b
    @params point: point to test
    @returns boolean value indictating membership.
    """
    def check_membership(self, point):
        assert len(point) == self.dim, "Point must be of the same dimension as system."
        
        for row_idx, row in enumerate(self.A):
            if np.dot(row, point) > self.b[row_idx]:
                return False
        return True

    """
    Calculate the enveloping box over the linear system
    @params model: input model
    @returns list of intervals representing edges of box.
    """
    def __calc_envelop_box(self):
        box_interval = []
        for i in range(self.dim):

            y = [0 for _ in range(self.dim)]
            y[i] = 1

            maxCood = self.max_opt(y).fun
            minCood = self.min_opt(y).fun
            box_interval.append([minCood, maxCood])

        return box_interval

    def __calc_box_volume(self, box_intervals):
        box_dim = [end - start for start,end in box_intervals]
        return reduce(mul, box_dim)

    """
    Sample a random point contained within a box.
    @params box_intervals: list of lists defining box
    @returns random point sampled within box
    """
    def __sample_box_point(self, box_intervals):
        assert len(box_intervals) == self.dim, "Number of intervals defining box must match dimension of system."

        return [ rand.uniform(start, end) for start, end in box_intervals ]

    """
    Generate random trajectories from polytope defined by parallelotope bundle.
    @params model: Model
            num_traj: umber of trajectories to generate.
            time_steps: number of time steps to generate trajs.
    @returns list of Traj objects representing num random trajectories.
    """
    def generate_traj(self, num_trajs, time_steps):
        initial_points = self.gen_ran_pts_box(num_trajs)
        trajs = [ Traj(self.model, point, steps=time_steps) for point in initial_points ]

        """
        if KaaSettings.use_parallel:
            'Parallelize point propagation'
            p = mp.Pool(processes=4)
            prop_trajs = p.starmap(point_prop, [ (model, point, time_steps) for point in initial_points ])
            p.close()
            p.join()
        """

        return TrajCollection(trajs)

    """
    Generates random points contained within the tightest enveloping parallelotope of the Chevyshev sphere.
    @params bund: Bundle object
            num_trajs: number of trajs to generate
            shrinkfactor: factor to shrink the radius of the sphere. This allows a box with smaller dimensions
    @returns list of generated random points.
    """
    def gen_ran_pts_box(self, num_trajs, shrinkfactor=1):
        chebycenter = self.chebyshev_center

        center = chebycenter.center
        radius = chebycenter.radius

        box_intervals = [[c - (radius*shrinkfactor), c + (radius*shrinkfactor)] for c in center]

        gen_points = []
        for _ in range(num_trajs):
            gen_points.append([rand.uniform(bound[0], bound[1]) for bound in box_intervals])

        return gen_points
