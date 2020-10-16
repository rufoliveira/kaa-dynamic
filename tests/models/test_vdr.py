from kaa.reach import ReachSet
from kaa.plotutil import Plot
from models.vanderpol import VanDerPol, VanDerPol_UnitBox

from kaa.temp.pca_strat import PCAStrat
from kaa.temp.lin_app_strat import LinStrat

from kaa.settings import PlotSettings
from kaa.timer import Timer
from kaa.trajectory import Traj

PlotSettings.save_fig = False

def test_VDP():

    NUM_STEPS = 4

    model = VanDerPol()
    unit_model = VanDerPol_UnitBox()

    #mod_reach = ReachSet(model)
    unit_mod_reach = ReachSet(unit_model)
    #mod_flow = mod_reach.computeReachSet(NUM_STEPS)

    VDP_PCA_ITER_STEPS = 1 #Number of steps between each recomputation of PCA Templates.
    'PCA Strategy Parameters'
    VDP_PCA_TRAJ_STEPS = 5 #Number of steps our sample trajectories should run.
    VDP_PCA_NUM_TRAJ = 1000 #Number of sample trajectories we should use for the PCA routine.

    pca_strat = PCAStrat(unit_model, traj_steps=VDP_PCA_TRAJ_STEPS, num_trajs=VDP_PCA_NUM_TRAJ, iter_steps=VDP_PCA_ITER_STEPS)
    mod_pca_flow = unit_mod_reach.computeReachSet(NUM_STEPS, tempstrat=pca_strat)


    points = [[0,1.90], [0.1, 1.90], [0.1,2], [0,2], [0.05,1.9], [0.05,2], [0,1.9],  [0,1.95], [0.1,1.95],  [0.01,1.99]]

    trajs = [Traj(unit_model, point ,NUM_STEPS) for point in points]
    vdp_plot = Plot()

    for traj in trajs:
        vdp_plot.add(traj)

    #vdp_plot.add(mod_flow, "VDP SAPO")
    vdp_plot.add(mod_pca_flow, "VDP PCA")
    vdp_plot.plot2DPhase(0,1, separate=True, plotvertices=True)

    Timer.generate_stats()


def test_lin_VDP():

    NUM_STEPS = 30

    model = VanDerPol()
    unit_model = VanDerPol_UnitBox()

    #mod_reach = ReachSet(model)
    unit_mod_reach = ReachSet(unit_model)
    #mod_flow = mod_reach.computeReachSet(NUM_STEPS)

    VDP_LIN_ITER_STEPS = 1 #Number of steps between each recomputation of PCA Templates.
    VDP_PCA_ITER_STEPS = 1 #Number of steps between each recomputation of PCA Templates.
    'PCA Strategy Parameters'
    VDP_PCA_TRAJ_STEPS = 5 #Number of steps our sample trajectories should run.
    VDP_PCA_NUM_TRAJ = 100 #Number of sample trajectories we should use for the PCA routine.

    pca_strat = LinStrat(unit_model, iter_steps=VDP_LIN_ITER_STEPS)
    mod_pca_flow = unit_mod_reach.computeReachSet(NUM_STEPS, tempstrat=pca_strat)

    vdp_plot = Plot()

    points = [[0,1.90], [0.1, 1.90], [0.1,2], [0,2], [0.05,1.9], [0.05,2], [0,1.9],  [0,1.95], [0.1,1.95],  [0.01,1.99]]

    trajs = [Traj(unit_model, point, NUM_STEPS) for point in points]
    vdp_plot = Plot()

    for traj in trajs:
        vdp_plot.add(traj)
    
    #vdp_plot.add(mod_flow)
    vdp_plot.add(mod_pca_flow, "VDP LinApp Strat")
    vdp_plot.plot2DPhase(0,1, separate=True, plotvertices=True)

    Timer.generate_stats()
