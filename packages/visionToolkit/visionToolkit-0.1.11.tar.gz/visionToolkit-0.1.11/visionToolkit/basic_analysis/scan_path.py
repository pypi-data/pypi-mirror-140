# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


from visionToolkit.basic_analysis import basic_processing as bp

class ScanPath():
    
    def __init__(self, 
                 df, sampling_frequency, 
                 size_plan_x = None,
                 size_plan_y = None,
                 distance_projection = 1000):


        nb_samples = len(df.iloc[:,0])
        delta_t = 1/sampling_frequency
        
        x_array = np.array(df.iloc[:,0])
        y_array = np.array(df.iloc[:,1])
        if len(df.columns) == 2:
            z_array = np.ones(len(df))*distance_projection
        elif len(df.columns) == 3:
            z_array = np.array(df.iloc[:,2])
            
        if size_plan_x == None:
            size_plan_x = abs(max(x_array) - min(x_array))
        if size_plan_y == None:
            size_plan_y = abs(max(y_array) - min(y_array))

        data_set = {'x_array': x_array,
                    'y_array': y_array,
                    'z_array': z_array,
                    'size_plan_x': size_plan_x,
                    'size_plan_y': size_plan_y,
                    'nb_samples': nb_samples,
                    'sampling_frequency': sampling_frequency}     
        
        basic_processing = bp.Basic_Processing(data_set)
        basic_processing.process()
        
        self.data_set = basic_processing.get_data_set()
        
    def get_data_set (self):
        return self.data_set