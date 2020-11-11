import numpy as np
from sklearn.decomposition import PCA

from kaa.templates import TempStrategy
from kaa.bundle import Bundle
from kaa.experiutil import generate_traj
from kaa.timer import Timer

"""
Implementation of creating templates through PCA
"""
class PCAStrat(TempStrategy):

    def __init__(self, model, traj_steps=5, num_trajs=100, iter_steps=10):
        super().__init__(model)

        self.traj_steps = traj_steps
        self.num_trajs = num_trajs
        self.iter_steps = iter_steps
        self.pca_ptope_queue = []

    def open_strat(self, bund):

        if not self.counter % self.iter_steps:
            #print(f"OPEN DIR/TEMP MAT: {bund.L},  {bund.T}")

            trajs = generate_traj(bund, self.num_trajs, self.traj_steps)
            traj_mat = np.empty((self.num_trajs, bund.dim))

            'Populate data matrix for PCA routine.'
            for traj_idx, traj in enumerate(trajs):
                traj_mat[traj_idx] = traj.end_point

            pca = PCA(n_components = self.model.dim)
            pca.fit(traj_mat)

            comps = pca.components_
            pca_dir_labels = [ str((self.counter, comp_idx)) for comp_idx, _ in enumerate(pca.components_) ]
            
            ptope_label = self.add_ptope_to_bund(bund, comps, pca_dir_labels)
            self.pca_ptope_queue.append(ptope_label)


    def close_strat(self, bund):

        if not self.counter % self.iter_steps:
            
            if self.counter:
                last_ptope = self.pca_ptope_queue.pop(0)
                self.rm_ptope_from_bund(bund, last_ptope)
                
            #print(self.pca_ptope_queue)
            #print("After:  L: {} \n T: {}".format(bund.L, bund.T))
            #print("After: offu: {} \n  offl: {}".format(bund.offu, bund.offl))

        #print("After:  L: {} \n T: {}".format(bund.L, bund.T))
        #print("After: offu: {} \n  offl: {}".format(bund.offu, bund.offl))

        self.counter += 1

    def __str__(self):
        return "PCAStrat-" if self.strat_order is None else f"PCAStrat{self.strat_order}-"


"""
Delayed PCA
"""
class DelayedPCAStrat(TempStrategy):

    def __init__(self, model, traj_steps=5, num_trajs=100, life_span=3):
        super().__init__(model)

        self.traj_steps = traj_steps
        self.num_trajs = num_trajs
        self.pca_ptope_life = []
        self.life_span = life_span

    def open_strat(self, bund):

        self.__add_new_ptope(bund)

    def close_strat(self, bund):

        'Remove dead templates'
        for ptope_label, life in self.pca_ptope_life:
            if life == 0:
                self.rm_ptope_from_bund(bund, ptope_label)

        self.pca_ptope_life = [(label, life-1) for label, life in self.pca_ptope_life if life > 0]

        #print("After:  L: {} \n T: {}".format(bund.L, bund.T))
        #print("After: offu: {} \n  offl: {}".format(bund.offu, bund.offl))

        self.counter += 1

    def __add_new_ptope(self, bund):

        new_pca_dirs, new_dir_labels = self.__generate_pca_dir(bund)
        new_ptope_label = self.add_ptope_to_bund(bund, new_pca_dirs, new_dir_labels)
        self.pca_ptope_life.append((new_ptope_label, self.life_span)) #Add fresh ptope and lifespan to step list

        return new_ptope_label

    def __generate_pca_dir(self, bund):
        
        trajs = generate_traj(bund, self.num_trajs, self.traj_steps)
        traj_mat = np.empty((self.num_trajs, bund.dim))

        'Populate data matrix for PCA routine.'
        for traj_idx, traj in enumerate(trajs):
            traj_mat[traj_idx] = traj.end_point

        pca = PCA(n_components = self.model.dim)
        pca.fit(traj_mat)

        ptope_dirs = [ str((self.counter, comp_idx)) for comp_idx, _ in enumerate(pca.components_) ]

        return pca.components_, ptope_dirs

        
    def __str__(self):
        return "DelayedPCAStrat-" if self.strat_order is None else f"PCAStrat{self.strat_order}-"
