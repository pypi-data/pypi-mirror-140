# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


class Angular_Coord():
    
    def __init__(self, 
                 data_set):

        self.nb_samples = data_set['nb_samples'] 
        self.data_set = data_set
     
              
    def angular_coord (self, x, y, z):
        
        size_plan_x = self.data_set['size_plan_x']
        size_plan_y = self.data_set['size_plan_y']
 
        x = x - size_plan_x/2
        y = y - size_plan_y/2

        results = {'angular_x_deg': (np.arctan(x/z)/(2*np.pi))*360,
                   'angular_y_deg': (np.arctan(y/z)/(2*np.pi))*360}
    
        return results
        
    
    def process_coord (self):
        
        results = self.angular_coord(self.data_set['x_array'],
                                     self.data_set['y_array'],
                                     self.data_set['z_array']) 
        
        smoothed_results = self.angular_coord(self.data_set['smoothed_x_array'],
                                              self.data_set['smoothed_y_array'],
                                              self.data_set['z_array'])
        
        self.data_set.update({'x_angle_deg': results['angular_x_deg'],
                              'y_angle_deg': results['angular_y_deg'],
                              'smoothed_x_angle_deg': smoothed_results['angular_x_deg'],
                              'smoothed_y_angle_deg': smoothed_results['angular_y_deg']})  
    
    
    def angular_speed (self, x_angle, y_angle):
        
        sampling = self.data_set['sampling_frequency']
        var_angle_x = x_angle[1:] - x_angle[:-1]
        var_angle_y = y_angle[1:] - y_angle[:-1]
        
        speeds = {'speeds_x': var_angle_x*sampling,
                  'speeds_y': var_angle_y*sampling}
        
        return speeds
        
        
    def process_speed (self):
        
        speeds_deg = self.angular_speed(self.data_set['x_angle_deg'], 
                                        self.data_set['y_angle_deg'])
        
        smoothed_speeds_deg = self.angular_speed(self.data_set['smoothed_x_angle_deg'], 
                                                 self.data_set['smoothed_y_angle_deg'])
        
        self.data_set.update({'x_angle_speed_deg': speeds_deg['speeds_x'],
                              'y_angle_speed_deg': speeds_deg['speeds_y'],
                              'smoothed_x_angle_speed_deg': smoothed_speeds_deg['speeds_x'],
                              'smoothed_y_angle_speed_deg': smoothed_speeds_deg['speeds_y']})  
        
        
    def absolute_angular_speed (self, x, y, z):
        
        size_plan_x = self.data_set['size_plan_x']
        size_plan_y = self.data_set['size_plan_y']
        sampling = self.data_set['sampling_frequency']
        
        x = x - size_plan_x/2
        y = y - size_plan_y/2
        
        gaze_vectors = np.concatenate((x.reshape(1,self.nb_samples),
                                       y.reshape(1, self.nb_samples), 
                                       z.reshape(1, self.nb_samples)), axis = 0)

        unitary_gaze_vectors = gaze_vectors/np.linalg.norm(gaze_vectors, axis = 0)
        
        absolute_angular_distances_rad = np.arccos(np.round(np.diag(np.matmul((unitary_gaze_vectors[:,:-1]).transpose(), 
                                                                               unitary_gaze_vectors[:,1:])),8))
        
        absolute_angular_distances_deg = np.abs(absolute_angular_distances_rad/(2*np.pi)*360)
        
        results = {'absolute_angular_distances_deg': absolute_angular_distances_deg,
                   'absolute_speeds_deg': absolute_angular_distances_deg * sampling,
                   'unitary_gaze_vectors': unitary_gaze_vectors}
       
        return results
        
        
    def process_absolute_speed (self):
        
        results = self.absolute_angular_speed(self.data_set['x_array'], 
                                              self.data_set['y_array'],
                                              self.data_set['z_array'])
        
        smoothed_results = self.absolute_angular_speed(self.data_set['smoothed_x_array'], 
                                                       self.data_set['smoothed_y_array'],
                                                       self.data_set['z_array'])
        
        self.data_set.update({'absolute_angular_distance_deg': results['absolute_angular_distances_deg'],
                              'absolute_speed_deg': results['absolute_speeds_deg'],
                              'unitary_gaze_vectors': results['unitary_gaze_vectors'],
                              'smoothed_absolute_angular_distance_deg': smoothed_results['absolute_angular_distances_deg'],
                              'smoothed_absolute_speed_deg': smoothed_results['absolute_speeds_deg'],
                              'smoothed_unitary_gaze_vectors': smoothed_results['unitary_gaze_vectors']})  


    def process (self):
        
        self.process_coord()
        self.process_speed()
        self.process_absolute_speed()
       
        
    def get_data_set (self):
        return self.data_set
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        