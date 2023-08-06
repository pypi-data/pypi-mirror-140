


import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter


class Microsaccades_Analysis():
    
    def __init__(self, 
                 data_set, lambda_threshold, 
                 smoothed, plot):

        self.nb_samples = data_set['nb_samples']
        
        self.data_set = data_set
        self.lambda_threshold = lambda_threshold
        
        self.smoothed = smoothed
        self.plot = plot
        
        self.speed_vectors = None
        self.where_is_ms = None
        
        self.sigma_x = None
        self.sigma_y = None
  
        self.result_set = {'physiological_variables': {}}
        
    
    def absolute_angular_distance(self, gaze_vect_1, gaze_vect_2):
        
        absolute_angular_distance_rad = np.arccos(np.round(np.matmul(gaze_vect_1, gaze_vect_2) ,8))
        absolute_angular_distance_deg = np.abs(absolute_angular_distance_rad/(2*np.pi)*360)
        
        return absolute_angular_distance_deg
          
    
    def find_ms (self, smoothed):
    
        if smoothed :
            self.speed_vectors = self.data_set['smoothed_speed_vectors']
        else :
            self.speed_vectors = self.data_set['speed_vectors']
    
        self.sigma_x = np.std(self.speed_vectors[:,0])*self.lambda_threshold
        self.sigma_y = np.std(self.speed_vectors[:,1])*self.lambda_threshold
    
        ms = np.zeros(self.nb_samples)
        for i in range (0, self.nb_samples):
            
            if ((self.speed_vectors[i,0]/(self.sigma_x))**2 
                + (self.speed_vectors[i,1]/(self.sigma_y))**2 > 1):
                ms[i] = 1
        
        is_ms = ms == 1.0
        self.where_is_ms = np.where(is_ms == True)[0]     
        ms_intervals = list()
        
        for k, g in groupby(enumerate(self.where_is_ms), lambda ix : ix[0] - ix[1]):
            ms_interval_local = list(map(itemgetter(1), g))
            ms_ends_local = [ms_interval_local[0], ms_interval_local[-1]]
            ms_intervals.append(ms_ends_local)
  
        results = {'is_microsaccade': is_ms,
                   'microsaccade_intervals': ms_intervals}
        
        return results   
  
    
    def basic_features(self, results):
        
        basic_features = {}
        
        if self.smoothed:
            x_coords = self.data_set['smoothed_x_array']
            y_coords = self.data_set['smoothed_y_array']
            unitary_gaze_vectors = self.data_set['smoothed_unitary_gaze_vectors']
        
        else:
            x_coords = self.data_set['x_array']
            y_coords = self.data_set['y_array'] 
            unitary_gaze_vectors = self.data_set['unitary_gaze_vectors']
            
        nb_saccades = len(results['microsaccade_intervals'])
        length = 0
        amplitude = 0
        
        for sac_int in results['microsaccade_intervals']:
            length += sac_int[-1] + 1 - sac_int[0] 
            amplitude += self.absolute_angular_distance(unitary_gaze_vectors[:,sac_int[0]], 
                                                        unitary_gaze_vectors[:,sac_int[-1]])
        
        mean_length = (length * 1000)/(nb_saccades * self.data_set['sampling_frequency'])
        mean_amplitude = amplitude/nb_saccades
        
        duration = self.nb_samples/self.data_set['sampling_frequency']
        frequency = nb_saccades/duration

        basic_features.update({'number of microsaccades:': nb_saccades,
                               'microsaccade mean duration (ms):': mean_length,
                               'microsaccade mean amplitude (degrees)': mean_amplitude,
                               'microsaccade frequency (/s)': frequency})
        
        return basic_features

        
    def process (self):
        
        results = self.find_ms(self.smoothed)
        basic_features = self.basic_features(results)
     
        self.result_set['physiological_variables']['microsaccades'] = {}
        self.result_set['physiological_variables']['microsaccades'].update({'is_microsaccade': results['is_microsaccade'],
                                                                            'microsaccade_intervals': results['microsaccade_intervals']})          
        
        print('\n\n-----------------------------------------------------------------------')
        print("Basic features for microsaccade analysis")
        print('-----------------------------------------------------------------------\n')

        for feature_name, value in basic_features.items():
            if type(value) == str:
                print("\t{0:40}\t {1}".format(feature_name, value))
            
            else:
                print("\t{0:40}\t {1}".format(feature_name, round(value,3)))
        if self.plot:
            self.plot_ms()
            
            
    def plot_ms (self):
        
        plt.style.use("seaborn")
        plt.scatter(self.speed_vectors[:,0], self.speed_vectors[:,1], 
                    s = 0.5,
                    color = 'cornflowerblue')
        plt.scatter(self.speed_vectors[self.where_is_ms, 0], 
                    self.speed_vectors[self.where_is_ms, 1], 
                    s = 0.6, 
                    color = 'indianred')
        t = np.linspace(0, 2*np.pi, 100)
        plt.plot(self.sigma_x * np.cos(t), self.sigma_y * np.sin(t), 
                 color = 'indianred', 
                 linewidth = 0.8)
        
        plt.xlim(-2.5*self.sigma_x, 2.5*self.sigma_x)
        plt.ylim(-2.5*self.sigma_y, 2.5*self.sigma_y)
        
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
    
        plt.xlabel("Horizontal speed", fontsize =9)
        plt.ylabel("Vertical speed", fontsize =9) 
        
        plt.show()
        plt.clf()
        

    def get_result_set (self):
        return self.result_set
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
