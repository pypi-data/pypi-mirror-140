# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from .velocity import Velocity_Analysis


class Phase_Plane_Analysis():

    def __init__(self,
                 data_set,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set

        self.delta_t = 1/data_set['sampling_frequency']

        self.result_set = {'statistical_variables': {}}
        self.plot = plot

        self.std_spd_x = None
        self.std_spd_y = None
        self.phase_plane_x = None
        self.phase_plane_y = None

    def RMS(array):
        return np.sqrt(np.mean(array**2))

    def compute_phase_plane_parameter(self):

        # Get velocity information
        vel = Velocity_Analysis(self.data_set, self.plot)
        vel.process()

        # STD SPD x
        mean_vx = np.mean(vel.velocity['v_x (px/s)'])
        std_spd_x = np.sqrt(np.mean(vel.velocity['v_x (px/s)']-mean_vx))

        # STD SPD y
        mean_vy = np.mean(vel.velocity['v_y (px/s)'])
        std_spd_y = np.sqrt(np.mean(vel.velocity['v_y (px/s)']-mean_vy))

        # Phase plane x
        phase_plane_x = np.sqrt(self.RMS(self.data_set['x_array'])**2 +
                                std_spd_x**2)

        # Phase plane y
        phase_plane_y = np.sqrt(self.RMS(self.data_set['y_array'])**2 +
                                std_spd_y**2)

        return std_spd_x, std_spd_y, phase_plane_x, phase_plane_y

    def process(self):

        self.std_spd_x, self.std_spd_y, \
            self.phase_plane_x, self.phase_plane_y = self.compute_phase_plane_parameter()

        self.result_set['statistical_variables']['dynamic'] = {
            'phase_plane': {}}
        self.result_set['statistical_variables']['dynamic']['phase_plane'] = (
            {'std_spd_x': self.std_spd_x,
             'std_spd_y': self.std_spd_y,
             'phase_plane_x': self.phase_plane_x,
             'phase_plane_y': self.phase_plane_y})

    def get_result_set(self):
        return self.result_set
