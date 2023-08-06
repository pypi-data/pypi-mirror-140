# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


class Gaze_Transition_Entropy():
    
    def __init__(self, 
                 in_AOI,
                 in_AOI_str,
                 in_AOI_str_ncr,
                 k_grams, simple_analysis = False):

        
        self.in_AOI = in_AOI
        self.nb_aoi = None
        self.simple_analysis = simple_analysis
        
        self.result_set = {'AOI_based_variables': {}}
        
        self.count_transitions = None
        self.transition_matrix = None
        self.statio_distrib = None
        
        self.shannon_entropy = None
        self.statio_distrib_entropy = None
        
        
    def compute_transition_matrix (self):
        
        seq_aoi = self.in_AOI
        
        u_aoi = set(seq_aoi)
        nb_aoi = len(u_aoi)
        self.nb_aoi = nb_aoi
        count_t = np.zeros((nb_aoi, nb_aoi))
    
        for i in range (1, len(seq_aoi)):
            from_aoi = int(seq_aoi[i-1])
            to_aoi = int(seq_aoi[i])
            count_t[from_aoi, to_aoi] += 1
  
        self.count_transitions = count_t
        
        sum_from = (1/np.sum(count_t, axis = 1)).reshape((nb_aoi,1))
        self.transition_matrix = np.matrix.round(count_t*sum_from, 3)

    
    def compute_statio_distribution (self) :            

        eig = np.linalg.eig(self.transition_matrix.T)
        eigvals = eig[0]
        vecs = eig[1]
   
        idx_pf = np.argmax(eigvals) 
        vec = vecs[:,idx_pf]
        
        self.statio_distrib = vec/np.sum(vec) 
        

    def compute_entropy (self) :
        
        transition_matrix = self.transition_matrix
        s_entropy = 0
        statio_entropy = 0
        for i in range (0, self.nb_aoi):
            if self.statio_distrib[i] != 0:
                statio_entropy -= self.statio_distrib[i] * np.log2(self.statio_distrib[i])
            local_entropy = 0
            for j in range (0, self.nb_aoi):
                if transition_matrix[i,j] != 0:
                    local_entropy += transition_matrix[i,j]*np.log2(transition_matrix[i,j])
            s_entropy -= self.statio_distrib[i] * local_entropy
            
        self.shannon_entropy = s_entropy
        self.statio_distrib_entropy = statio_entropy
        
        
    def process (self):
        
        self.compute_transition_matrix()
        self.compute_statio_distribution()
        self.compute_entropy()
    
        self.result_set['AOI_based_variables'].update({'gaze_transtion_entropy': {}})
        self.result_set['AOI_based_variables']['gaze_transtion_entropy'].update({'transition_matrix': self.transition_matrix,
                                                                                 'stationary_distribution': self.statio_distrib,
                                                                                 'shannon_entropy': self.shannon_entropy,
                                                                                 'stationary_distribution_entropy': self.statio_distrib_entropy}) 
        
        if self.simple_analysis:
        
            print('\n\n-----------------------------------------------------------------------')
            print("Transition Matrix Analysis")
            print('-----------------------------------------------------------------------\n')
            print("\t{0:40}\t {1}".format('transition_matrix', self.transition_matrix[0,:]))
            for i in range (1, self.nb_aoi):
                print("\t{0:40}\t {1}".format('_____', self.transition_matrix[i,:]))
        else:
            to_export = {'shannon_entropy': self.shannon_entropy,
                         'stationary_distribution_entropy': self.statio_distrib_entropy}
        
            print('\n\n-----------------------------------------------------------------------')
            print("Gaze Transition Entropy Analysis")
            print('-----------------------------------------------------------------------\n')
            

            for feature_name, value in to_export.items():
                print("\t{0:40}\t {1}".format(feature_name, np.round(value,3)))
                #print("\t{0:40}\t {1}".format(feature_name, round(value,3)))
                    
                
                
    def get_result_set (self):
        return self.result_set
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
