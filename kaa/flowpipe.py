import matplotlib.pyplot as plt
import numpy as np

from kaa.timer import Timer
from kaa.settings import PlotSettings
from kaa.templates import MultiStrategy

"""
Object encapsulating flowpipe data. A flowpipe in this case will be a sequence of Bundle objects.
"""
class FlowPipe:

    def __init__(self, flowpipe, model, strat):

        self.flowpipe = flowpipe
        self.model = model
        self.strat = strat
        self.vars = model.vars
        self.dim = model.dim
        self.length = len(self.flowpipe)

    """
    Returns a list of strategies which were acting during the reachable set
    computation producing this flowpipe. The strategies are in acting order supplied into
    MultiStrategy.
    """
    @property
    def strats(self):
        return self.strat.strat_list if isinstance(self.strat, MultiStrategy) else [self.strat]

    @property
    def model_name(self):
        return self.model.name

    """
    Returns accumlation sum of the bundle volumes
    """
    @property
    def total_volume(self):
        return np.sum(self.get_volume_data())

    def get_strat_flowpipe(self, strat):
        strat_flowpipe = []

        for bund_idx, bund in enumerate(self.flowpipe):
            ptope_strat_list = bund.get_ptopes_by_strat(strat)

            #assert len(ptope_strat_list) != 0, f"Input Strategy must act on bundle object at index {bund_idx}"
            strat_flowpipe.append(ptope_strat_list[0]) #Get first one for now

        return strat_flowpipe

    """
    Returns array of volume data for each bundle in the flowpipe.
    @returns array of volume data.
    """
    def get_volume_data(self):
        vol_data = np.empty(self.length)
        for idx, bund in enumerate(self.flowpipe):
            vol_data[idx] = bund.getIntersect().volume

        return vol_data
    
    """
    Calculates the flowpipe projection of reachable set against time t.
    @params var: The variable for the reachable set to be projected onto.
    @returns list of minimum and maximum points of projected set at each time step.
    """
    def get2DProj(self, var_ind):
        pipe_len = len(self.flowpipe)

        Timer.start('Proj')
        curr_var = self.vars[var_ind]

        'Vector of minimum and maximum points of the polytope represented by parallelotope bundle.'
        y_min, y_max = np.empty(pipe_len), np.empty(pipe_len)

        'Initialize objective function'
        y_obj = [0 for _ in self.vars]
        y_obj[var_ind] = 1

        'Calculate the minimum and maximum points through LPs for every iteration of the bundle.'
        for bund_ind, bund in enumerate(self.flowpipe):

            bund_sys = bund.getIntersect()

            y_min[bund_ind] = bund_sys.max_opt(y_obj).fun
            y_max[bund_ind] = bund_sys.min_opt(y_obj).fun

        Timer.stop("Proj")

        return y_min, y_max

    def __len__(self):
        return self.length

    def __iter__(self):
        return iter(self.flowpipe)

    def __str__(self):
        return "{} Len: {}".format(self.strat, len(self))
