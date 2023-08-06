# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from visionToolkit.basic_analysis import smoothing as smg
from visionToolkit.basic_analysis import angular_coord as acd




class Basic_Processing():
    
    def __init__(self, data_set): 
        
        self.data_set = data_set
        
        
    def process (self):
        
        #print("Processing basic analysis")
       
        smoothing = smg.Smoothing(self.data_set)
        smoothing.process()
        self.data_set = smoothing.get_data_set()

        angular_coord = acd.Angular_Coord(self.data_set)
        angular_coord.process()
        self.data_set = angular_coord.get_data_set()
    
        
    def get_data_set (self):
        return self.data_set