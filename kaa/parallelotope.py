import numpy as np
import multiprocessing as mp
import random

from kaa.lputil import minLinProg, maxLinProg
from kaa.timer import Timer
from kaa.settings import KaaSettings


class LinearSystem:

    def __init__(self, A, b, vars):
        self.A = A
        self.b = b
        self.vars = vars
        self.dim = len(vars)

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
        return np.asarray(center_pt[:-1])



"""
Object encapsulating routines calculating properties of parallelotopes.
"""
class Parallelotope(LinearSystem):

    def __init__(self, A, b, vars):
        super().__init__(A, b, vars)
        self.u_A = A[:self.dim]
        self.u_b = b[:self.dim]

    """
    Return list of functions transforming the n-unit-box over the parallelotope.
    @returns list of transfomation from unitbox over the parallelotope.
    """
    def getGeneratorRep(self):

        Timer.start('Generator Procedure')
        base_vertex = self._computeBaseVertex()
        gen_list = self._computeGenerators(base_vertex)

        'Create list representing the linear transformation q + \sum_{j} a_j* g_j'
        expr_list = base_vertex
        for j in range(self.dim):
            for var_ind, var in enumerate(self.vars):
                expr_list[j] += gen_list[var_ind][j] * var
        Timer.stop('Generator Procedure')

        return expr_list
    
    """
    Calculate generators as substraction: vertices - base_vertex.
    We calculate the vertices by solving the following linear system for each vertex i:


    Ax = [b_1, ... , -b_{i+n}, ... , b_n]^T

    Note that this simply finds the vertex to calculate the generator vectors. The generators will be the vectors g_j = v_j - q
    where v_j is the jth vertex calculated in the manner above.

    The parallelotope will be exprssed as sum of the base vertex and the convex combination of the generators.

    p(a_1, ... ,a_n) =  q + \sum_{j} a_j * g_j

    where q is the base vertex and the g_j are the generators. a_j will be in the unitbox [0,1]

    @params base_vertex: base vertex q
    @returns generator vectors g_j
    """
    def _computeGenerators(self, base_vertex):
        
        'Hacky way to toggle parallelism for experiments'
        if KaaSettings.use_parallel:
            p = mp.Pool(processes=4)
            vertices = p.starmap(self._gen_worker, [ (i, u_b, coeff_mat) for i in range(self.dim) ])
            p.close()
            p.join()
        else:
            vertices = []
            for i in range(self.dim):
               vertices.append(self._gen_worker(i, self.u_b, self.u_A))

        vertex_list = [ [vert - base for vert, base in zip(vertices[i], base_vertex)] for i in range(self.dim) ]
        #print("Vertex List For Paratope: {} \n".format(vertices))
        #print("Vector List For Paratope: {} \n".format(vertex_list))
        return vertex_list

    """
    Worker process for calculating vertices of higher-dimensional parallelotopes.
    Only called by Pool.starmap
    @params i - vertex index
            u_b, coef_mat - shared reference to upper offsets and directions matrix.
    @returns coordinates of vertex
    """
    def _gen_worker(self, i, u_b, coeff_mat):
        #print(coeff_mat, u_b)

        negated_bi = np.copy(self.u_b)
        negated_bi[i] = -self.b[i + self.dim]
        #print("(coeff_mat, negated_bi): {}".format((coeff_mat, negated_bi)))
        sol_set_i = np.linalg.solve(coeff_mat, negated_bi)

        return list(sol_set_i)

    """
    Calculate the base vertex of the parallelotope (variable q)
    We calculate the vertices by solving a linear system of the following form:

    Ax = u_b

    where u_b are the offsets for the upper facets of parallelotope (first half of self.b).

    @returns base-vertex in list
    """
    def _computeBaseVertex(self):

        sol_set = np.linalg.solve(self.u_A, self.u_b)
        return list(sol_set)


    """
    Convert numpy matrix into sympy matrix
    @params mat: numpy matrix
    @returns sympy matrix counterpart
    """
    def _convertMatFormat(self, mat):
        return sp.Matrix(mat.tolist())

    """
    Takes solution set returned by sympy and converts into list
    @params fin_set: FiniteSet
    @returns list of sympy solution set
    """
    def _convertSolSetToList(self, fin_set):

        assert fin_set is not sp.EmptySet

        return list(fin_set.args[0])
    
    """
    Generate list of random points contained inside the parallelotope.
    @params: num_points: number of points to generate.
    @returns list of random points contained inside parallelotope.
    """
    def gen_random_pt(self):

        gen_expr = self.getGeneratorRep()

        interval_ran_pts = [ (var, random.uniform(0,1)) for var in self.vars ]
        return [ expr.subs(interval_ran_pts, simultaneous=True) for expr in gen_expr ]
