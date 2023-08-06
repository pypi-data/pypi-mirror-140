# -*- coding: utf-8 -*-

import numpy as np


class Sway_Area_ps():

    def __init__(self,
                 data_set,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set

        self.delta_t = 1/data_set['sampling_frequency']

        self.result_set = {'statistical_variables': {}}
        self.plot = plot

        self.saps = None

    def sway_area_per_second(self):

        T = self.nb_samples
        column1 = self.data_set['x_array'][1:] * \
            self.data_set['y_array'][:-1]
        column2 = self.data_set['x_array'][:-1] * \
            self.data_set['y_array'][1:]

        return 1/(2*T)*np.sum(np.abs(column1-column2))

    def process(self):

        self.saps = self.sway_area_per_second()

        self.result_set['statistical_variables']['dynamic'] = {
            'sway_area_per_second': {}}
        self.result_set['statistical_variables']['dynamic']['sway_area_per_second'] = (
            {'saps': self.saps})

    def get_result_set(self):
        return self.result_set
