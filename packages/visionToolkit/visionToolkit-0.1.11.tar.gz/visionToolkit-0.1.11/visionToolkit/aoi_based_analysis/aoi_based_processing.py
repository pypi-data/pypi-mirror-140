# -*- coding: utf-8 -*-



import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from itertools import groupby


from visionToolkit.aoi_based_analysis import n_gram as nga
from visionToolkit.aoi_based_analysis import gaze_transition_entropy as gte
from visionToolkit.aoi_based_analysis import lempei_ziv_complexity as lzc


class AOI_Based_Processing():
    
    def __init__(self, data_set, AOIs,
                 initial_reduction, k_grams,
                 method, plot, simple_analysis = False):

        self.nb_samples = len(data_set['x_array'])        
        self.data_set = data_set
        
        self.input_AOIs = AOIs
        self.nb_AOIs = len(AOIs)
        self.plot = plot
        self.simple_analysis = simple_analysis
        
        self.method = method
        self.dict_methods = {'N_Gram': nga.N_Gram,
                             'GTE': gte.Gaze_Transition_Entropy,
                             'LZC': lzc.Lempei_Ziv_Complexity}

        self.initial_reduction = initial_reduction
        self.k_grams = k_grams
        
        self.in_AOI = None
        self.in_AOI_str = None
        self.in_AOI_str_ncr = None
        
        self.x_red = None
        self.y_red = None
        self.nb_samples_red = None
        
        self.result_set = None



    def in_ellipsis (self, x, y, ellipsis) :
        
        theta_rad = ellipsis[4]*np.pi/180
        d = (((x-ellipsis[0])*np.cos(theta_rad) + (y-ellipsis[1])*np.sin(theta_rad))**2/ellipsis[2]**2 
             + ((x-ellipsis[0])*np.sin(theta_rad) - (y-ellipsis[1])*np.cos(theta_rad))**2/ellipsis[3]**2)
        
        if d > 1:
            return False
        else :
            return True
        
        
        
    def reduction (self, k):
        
        nb_samples_red = self.nb_samples//k
        
        x_red = np.zeros(nb_samples_red)
        y_red = np.zeros(nb_samples_red)
        
        for i in range (0, nb_samples_red):
            x_red[i] = np.mean(self.data_set['x_array'][i*k: (i+1)*k])
            y_red[i] = np.mean(self.data_set['y_array'][i*k: (i+1)*k])
        
        self.x_red = x_red
        self.y_red = y_red
        
        self.nb_samples_red = nb_samples_red
        

        
    def process_aoi (self):
        
        AOIs = self.input_AOIs      
        in_aoi = np.zeros(self.nb_samples_red)
        
        x = self.x_red
        y = self.y_red
        #plt.plot(x, y)
        
        for i in range (0, self.nb_samples_red):
            found = False
            k = 1
            
            x_l = x[i]
            y_l = y[i]
            while found == False and k <= self.nb_AOIs :
                if self.in_ellipsis(x_l, y_l, AOIs[k-1]) :
                    in_aoi[i] = int(k)
                    found = True
                k+=1
  
        self.in_AOI = in_aoi
        in_aoi_str = []
        
        for j in range (0, len(in_aoi)):
            in_aoi_str.append(chr(int(64+in_aoi[j])))
        
        in_aoi_str_no_cons_rep = [i[0] for i in groupby(in_aoi_str)]
        
        self.in_AOI_str = ''.join(in_aoi_str)
        self.in_AOI_str_ncr = ''.join(in_aoi_str_no_cons_rep)
        #print("AOI processed")
     
   
    
    def process (self):
        
        self.reduction(self.initial_reduction)      
        self.process_aoi()        
        
        analysis = self.dict_methods[self.method](self.in_AOI,
                                                  self.in_AOI_str,
                                                  self.in_AOI_str_ncr,
                                                  self.k_grams,
                                                  self.simple_analysis)   
        analysis.process()
        
        self.result_set = analysis.get_result_set()
        
        x = self.x_red
        y = self.y_red
        if self.plot:
            
            for i in range (0, len(self.in_AOI)):
                a_1 = np.where(self.in_AOI == i+1)
                plt.scatter(x[a_1], y[a_1], 
                            color = 'blue',
                            s=4)
            
            plt.plot(x, y, linewidth=0.2)
            t = np.linspace(0, 2*np.pi, 100)
    
            for i in range (0, self.nb_AOIs):
                ellipsis = self.input_AOIs[i]
                theta_rad = ellipsis[4]*np.pi/180
             
                
                Ell = np.array([ellipsis[2]*np.cos(t) , ellipsis[3]*np.sin(t)])  
                R_rot = np.array([[np.cos(theta_rad), -np.sin(theta_rad)],
                                  [np.sin(theta_rad), np.cos(theta_rad)]])  
               
                Ell_rot = np.zeros((2,Ell.shape[1]))
                for i in range(Ell.shape[1]):
                    Ell_rot[:,i] = np.dot(R_rot,Ell[:,i])
                
                plt.plot(ellipsis[0] + Ell_rot[0,:] , ellipsis[1] + Ell_rot[1,:],
                         color = 'indianred',
                         linewidth = 1.0) 
            
            plt.xlim((850,950))
            plt.ylim((300,400))
            plt.show()
            plt.clf()
            

    def get_result_set (self):
        return self.result_set

    
        
def NGram (scan_path, AOIs, 
           k_grams = 3, initial_reduction = 2, discard_order = False,
           plot = True):
    
    data_set = scan_path.get_data_set()
    aoi_processing = AOI_Based_Processing(data_set, AOIs, 
                                          initial_reduction, k_grams,
                                          'N_Gram', plot)   
    aoi_processing.process()
    result_set = aoi_processing.get_result_set() 
    
    if discard_order:
        results = result_set['AOI_based_variables']['N_Gram']['results_od']
    else : 
        results = result_set['AOI_based_variables']['N_Gram']['results']
    
    return results

    

def TransitionMatrix (scan_path, AOIs, 
                      initial_reduction = 2,
                      plot = True):
     
    data_set = scan_path.get_data_set()
    aoi_processing = AOI_Based_Processing(data_set, AOIs, 
                                          initial_reduction, 3,
                                          'GTE', plot, simple_analysis = True)      
    aoi_processing.process()
    result_set = aoi_processing.get_result_set() 
    
    transition_matrix = result_set['AOI_based_variables']['gaze_transtion_entropy']['transition_matrix']

    return transition_matrix



def GTE (scan_path, AOIs, 
         initial_reduction = 2,
         plot = True):
    
    data_set = scan_path.get_data_set()
    aoi_processing = AOI_Based_Processing(data_set, AOIs, 
                                          initial_reduction, 3,
                                          'GTE', plot)      
    aoi_processing.process()
    result_set = aoi_processing.get_result_set() 
    
    shannon_entropy = result_set['AOI_based_variables']['gaze_transtion_entropy']['shannon_entropy']
    statio_dist_entropy = result_set['AOI_based_variables']['gaze_transtion_entropy']['stationary_distribution_entropy']
    
    return shannon_entropy, statio_dist_entropy
      
      
      
def LempeiZiv (scan_path, AOIs, 
               initial_reduction = 2,
               plot = True):
    
    data_set = scan_path.get_data_set()
    aoi_processing = AOI_Based_Processing(data_set, AOIs, 
                                          initial_reduction, 3,
                                          'LZC', plot)       
    aoi_processing.process()
    result_set = aoi_processing.get_result_set() 
      
    complexity = result_set['AOI_based_variables']['lempei_ziv_complexity']['complexity']
    decomposition = result_set['AOI_based_variables']['lempei_ziv_complexity']['decomposition']
    
    return complexity, decomposition      
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        