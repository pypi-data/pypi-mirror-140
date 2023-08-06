# -*- coding: utf-8 -*-

import numpy as np
from .velocity import Velocity_Analysis


class Mean_Frequency():

    def __init__(self,
                 data_set,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set

        self.delta_t = 1/data_set['sampling_frequency']

        self.result_set = {'statistical_variables': {}}
        self.plot = plot

        self.mean_freq_x = None
        self.mean_freq_y = None
        self.mean_frequency = None

    def mean_dist(self):

        mean_dist_x = np.mean(np.abs(self.data_set['x_array']))
        mean_dist_y = np.mean(np.abs(self.data_set['y_array']))
        mean_dist = np.mean(np.sqrt(self.data_set['x_array']**2 +
                                    self.data_set['y_array']**2))

        return mean_dist_x, mean_dist_y, mean_dist

    def mean_frequency(self):

        # Get velocity information
        vel = Velocity_Analysis(self.data_set, self.plot)
        vel.process()

        # Mean SPD computation
        spd_x, spd_y, spd_tot = vel.spd_x, vel.spd_y, vel.spd_tot

        # Mean Dist computation
        mean_dist_x, mean_dist_y, mean_dist = self.mean_dist()

        # Mean freq x
        mean_freq_x = (1/4/np.sqrt(2))*spd_x/mean_dist_x

        # Mean freq y
        mean_freq_y = (1/4/np.sqrt(2))*spd_y/mean_dist_y

        # Mean freq total
        mean_freq = (1/2/np.pi)*spd_tot/mean_dist

        return mean_freq_x, mean_freq_y, mean_freq

    def process(self):

        self.mean_freq_x, self.mean_freq_y, self.mean_freq = self.mean_frequency()

        self.result_set['statistical_variables']['dynamic'] = {
            'mean_frequency': {}}
        self.result_set['statistical_variables']['dynamic']['mean_frequency'] = (
            {'mean_freq_x': self.mean_freq_x,
             'mean_freq_y': self.mean_freq_y,
             'mean_freq': self.mean_freq})

    def get_result_set(self):
        return self.result_set
