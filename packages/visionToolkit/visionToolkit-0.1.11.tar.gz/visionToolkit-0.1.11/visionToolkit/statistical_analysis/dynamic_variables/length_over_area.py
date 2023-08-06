# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from .velocity import Velocity_Analysis
# from ..positional_variables.conf_area import ConfidenceArea


class LFS_Analysis():

    def __init__(self,
                 data_set,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set

        self.delta_t = 1/data_set['sampling_frequency']

        self.result_set = {'statistical_variables': {}}
        self.plot = plot

        self.lfs = None

    def LFS(self):
        """
        Requires 95% conf area from the positional variables
        """

        # Get velocity information
        vel = Velocity_Analysis(self.data_set, self.plot)
        vel.process()

        # TO BE MODIFIED
        # conf_area = ConfidenceArea(self.data_set)
        conf_area = np.pi

        return vel.sl_tot/conf_area

    def process(self):
        
        self.lfs = self.LFS()

        self.result_set['statistical_variables']['dynamic'] = {'lfs': {}}
        self.result_set['statistical_variables']['dynamic']['lfs'] = ({
                                                                      'lfs': self.lfs})

    def get_result_set(self):
        return self.result_set
