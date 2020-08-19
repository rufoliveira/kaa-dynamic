from kaa.reach import ReachSet
from kaa.plotutil import Plot
from models.sir import SIR

from kaa.timer import Timer
from kaa.experiutil import generate_traj

def test_SIR():

    model = SIR()
    trajs = generate_traj(model, 10, 200)
    mod_reach = ReachSet(model)
    mod_flow = mod_reach.computeReachSet(200)

    sir_plot = Plot()
    #trajs = generate_traj(model, 10, 200)

    'Generaste the trajectories and add them to the plot.'
    for traj in trajs:
        sir_plot.add(traj)

    sir_plot.add(mod_flow)
    sir_plot.plot(0)
    
    Timer.generate_stats()
