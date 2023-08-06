# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd



class Smoothing():
    
    def __init__(self, data_set):
        
        self.x_array = data_set['x_array']
        self.y_array = data_set['y_array']
        
        self.nb_samples = data_set['nb_samples']
        self.delta_t = 1/data_set['sampling_frequency'] 
        
        self.data_set = data_set
        
        
    def generate_speed_vectors (self):
        
        speed_vectors = np.zeros((self.nb_samples, 2))    
        positions = np.concatenate((self.x_array.reshape(1, self.nb_samples), 
                                    self.y_array.reshape(1, self.nb_samples)))
        for i in range (0, self.nb_samples -1):
            local_speed = (positions[:, i+1] - positions[:, i])/(self.delta_t)
            speed_vectors[i] = local_speed
        self.data_set['speed_vectors'] = speed_vectors
    

    def generate_smoothed_speed_vectors (self):
            
        speed_vectors = np.zeros((self.nb_samples, 2))    
        positions = np.concatenate((self.x_array.reshape(1, self.nb_samples), 
                                    self.y_array.reshape(1, self.nb_samples)))
        
        for i in range (2, self.nb_samples -2):

            local_speed = ((positions[:, i+2] + positions[:, i+1] 
                            -positions[:, i-1] - positions[:, i-2])
                           /(6 * self.delta_t))
            speed_vectors[i] = local_speed
                
        speed_vectors[1] = ((positions[:, 2] 
                            - positions[:, 0]) 
                            / (2 * self.delta_t))
        speed_vectors[0] = speed_vectors[1]
        speed_vectors[self.nb_samples -2] = ((positions[:, self.nb_samples - 1]
                                              -positions[:, self.nb_samples - 3])
                                             /(2 * self.delta_t))
        speed_vectors[self.nb_samples - 1] = speed_vectors[self.nb_samples -2]     
        self.data_set['smoothed_speed_vectors'] = speed_vectors
      

    def generate_smoothed_positions(self):
        
        smoothed_x_array = np.zeros(self.nb_samples)
        smoothed_y_array = np.zeros(self.nb_samples)
        
        smoothed_speed_vectors = self.data_set['smoothed_speed_vectors']
        
        smoothed_x_array[0] = self.x_array[0]
        smoothed_y_array[0] = self.y_array[0]
        
        for i in range (1, self.nb_samples):
            smoothed_x_array[i] = (smoothed_x_array[i-1] 
                                   + smoothed_speed_vectors[i-1, 0] * self.delta_t)
            smoothed_y_array[i] = (smoothed_y_array[i-1] 
                                   + smoothed_speed_vectors[i-1, 1] * self.delta_t)                   
        self.data_set.update({'smoothed_x_array': smoothed_x_array,
                              'smoothed_y_array': smoothed_y_array})
    
    
    def process (self):
        
        self.generate_speed_vectors()
        self.generate_smoothed_speed_vectors()
        self.generate_smoothed_positions()


    def get_data_set (self):
        return self.data_set


