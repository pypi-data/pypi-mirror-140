# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from scipy import signal

import matplotlib.pyplot as plt



class Welch_Analysis():
    
    def __init__(self, 
                 data_set, 
                 nb_per_seg, daya_type,
                 smoothed, plot):

        self.nb_samples = data_set['nb_samples']-1
        
        self.data_set = data_set        
        self.data_type = daya_type
        self.nb_per_seg = nb_per_seg
        
        self.smoothed = smoothed
        self.plot = plot
         
        self.result_set = {'statistical_variables': {}}
        
        self.frequencies_Welch = {}
        self.periodogramme_Welch = {}
    
        
    def Welch_periodogramme (self, data, direction):
    
        frequencies_Welch = {}
        periodogramme_Welch = {} 
              
        self.frequencies_Welch[direction], self.periodogramme_Welch[direction] = signal.welch(data, 
                                                                                              self.data_set['sampling_frequency'], 
                                                                                              nperseg = self.nb_per_seg, 
                                                                                              scaling = 'density')

    def process (self):
        
        if self.smoothed:
            if self.data_type == 'position':
                data_x = self.data_set['smoothed_x_array']
                data_y = self.data_set['smoothed_y_array']
                
            elif self.data_type == 'speed':
                data_x = self.data_set['smoothed_speed_vectors'][:,0]
                data_y = self.data_set['smoothed_speed_vectors'][:,1]
                
        else :
            if self.data_type == 'position':
                data_x = self.data_set['x_array']
                data_y = self.data_set['y_array']
                
            elif self.data_type == 'speed':
                data_x = self.data_set['speed_vectors'][:,0]
                data_y = self.data_set['speed_vectors'][:,1]
                
        self.Welch_periodogramme(data_x, 'x')
        self.Welch_periodogramme(data_y, 'y')  
        
        self.result_set['statistical_variables']['frequency'] = {}
        self.result_set['statistical_variables']['frequency']['Welch'] = ({'frequencies': self.frequencies_Welch['x'],
                                                                           'periodogramme_horizontal': self.periodogramme_Welch['x'],
                                                                           'periodogramme_vertical': self.periodogramme_Welch['y']})
        
                
        if self.plot:
            self.plot_periodogram()

        
    def plot_periodogram(self, direction = 'both'):

        plt.style.use("seaborn")
  
        fig, axs = plt.subplots(1, 2, figsize=(12,5))
        if self.data_type == 'position':
            fig.suptitle('Position Welch Periodograms')
        
        elif self.data_type == 'speed':
            fig.suptitle('Speed Welch Periodograms')
        
        axs[0].plot(self.frequencies_Welch['x'], self.periodogramme_Welch['x'], 
                    linewidth = 0.5,
                    color = 'cornflowerblue')
        
        axs[0].set_title('Horizontal axis')
        
        axs[1].plot(self.frequencies_Welch['y'], self.periodogramme_Welch['y'], 
                    linewidth = 0.5,
                    color = 'indianred')
        
        axs[1].set_title('Vertical axis')

        
        for ax in axs.flat:
            ax.set(xlabel='Frequency (Hz)', ylabel='Spectrum',)        
               
        plt.show()
        plt.clf()         
                
                
    def get_result_set (self):
        return self.result_set               
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                