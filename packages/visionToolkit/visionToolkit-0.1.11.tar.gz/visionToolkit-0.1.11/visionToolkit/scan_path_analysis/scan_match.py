# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.spatial import distance


class ScanMatch_Analysis():
    
    
    def __init__(self, 
                 data_set_1, data_set_2,
                 smoothed, concordance_bonus, gap_penalty, 
                 h_size, v_size,
                 plot):
        

        self.data_set_1 = data_set_1
        self.data_set_2 = data_set_2
        
        self._n_s1 = data_set_1['nb_samples']
        self._n_s2 = data_set_2['nb_samples']
        
        self.smoothed = smoothed
        self.result_set = {'scan_path_variables': {}}
        
        _sequence_1 = np.zeros((data_set_1['nb_samples'], 2))
        _sequence_2 = np.zeros((data_set_2['nb_samples'], 2))
        
        if smoothed :
            _sequence_1[:,0] = data_set_1['smoothed_x_array']
            _sequence_1[:,1] = data_set_1['smoothed_y_array']
            _sequence_2[:,0] = data_set_2['smoothed_x_array']
            _sequence_2[:,1] = data_set_2['smoothed_y_array']
        else :
            _sequence_1[:,0] = data_set_1['x_array']
            _sequence_1[:,1] = data_set_1['y_array']
            _sequence_2[:,0] = data_set_2['x_array']
            _sequence_2[:,1] = data_set_2['y_array']

        self._sequence_1 = _sequence_1
        self._sequence_2 = _sequence_2
        
        self.plot = plot
      
        self.x_box_size = None
        self.y_box_size = None
        
        self.concordance_bonus = concordance_bonus
        self.gap_penalty = gap_penalty
        
        self.nb_loc_x = h_size
        self.nb_loc_y = v_size
        
        self._loc_1 = None
        self._loc_2 = None
        
        self.d_str_seq_1 = None
        self.d_str_seq_2 = None
        
        
      
    def pre_process (self):
        
        assert self.data_set_1['size_plan_x'] == self.data_set_2['size_plan_x'], 'Plans have different sizes'
            


        x_max = max(np.max(self._sequence_1[:,0]), np.max(self._sequence_2[:,0]))
        x_min = min(np.min(self._sequence_1[:,0]), np.min(self._sequence_2[:,0]))
        
        y_max = max(np.max(self._sequence_1[:,1]), np.max(self._sequence_2[:,1]))
        y_min = min(np.min(self._sequence_1[:,1]), np.min(self._sequence_2[:,1]))
        
        if self.concordance_bonus == None:
            self.concordance_bonus = 0.1*(np.sqrt((x_max-x_min)**2 + (y_max-y_min)**2))
        
        self.x_box_size = (x_max - x_min)/self.nb_loc_x + 0.1
        self.y_box_size = (y_max - y_min)/self.nb_loc_y + 0.1
        
        _loc_1 = np.zeros((self._n_s1, 2), dtype = np.int32)
        _loc_2 = np.zeros((self._n_s2, 2), dtype = np.int32)
        
        _loc_1[:,0] = ((self._sequence_1[:,0] - x_min) * (1/self.x_box_size)).astype(int)
        _loc_1[:,1] = ((self._sequence_1[:,1] - y_min) * (1/self.y_box_size)).astype(int)
        
        _loc_2[:,0] = ((self._sequence_2[:,0] - x_min) * (1/self.x_box_size)).astype(int)
        _loc_2[:,1] = ((self._sequence_2[:,1] - y_min) * (1/self.y_box_size)).astype(int)
        
        self._loc_1 = _loc_1
        self._loc_2 = _loc_2
        
        seq_str_1 = []
        seq_str_2 = []
        
        for i in range(0, self._n_s1):
            local_str = chr(65+_loc_1[i,1]) + chr(65+_loc_1[i,0])
            seq_str_1.append(local_str)
            
        for i in range(0, self._n_s2):
            local_str = chr(65+_loc_2[i,1]) + chr(65+_loc_2[i,0])
            seq_str_2.append(local_str)
        
        self.d_str_seq_1 = seq_str_1
        self.d_str_seq_2 = seq_str_2
      
        
  
    def distance_e (self, lig_1, lig_2, col_1, col_2):
        
        a = (col_1*self.x_box_size, lig_1*self.y_box_size)
        b = (col_2*self.x_box_size, lig_2*self.y_box_size)
        
        return self.concordance_bonus/2 - np.sqrt(distance.euclidean(a, b))
    
        
    
    def compute_substitution_matrix (self):
        
        concordance_bonus = self.concordance_bonus
        nb_loc_x = self.nb_loc_x
        nb_loc_y = self.nb_loc_y
        
        subst_matrix = np.zeros((self.nb_loc_x*self.nb_loc_y, self.nb_loc_x*self.nb_loc_y))
        for i in range (0, nb_loc_x*nb_loc_y):
            subst_matrix[i,i] = concordance_bonus
            
            for j in range (0, i):
                _lig_1 = i//nb_loc_x
                _lig_2 = j//nb_loc_x
                
                _col_1 = i%nb_loc_x
                _col_2 = j%nb_loc_x
                
                subst_matrix[i,j] = self.distance_e(_lig_1, _lig_2, _col_1, _col_2)
            
        for i in range (0, nb_loc_x*nb_loc_y):
            for j in range (i+1, nb_loc_x*nb_loc_y):
                subst_matrix[i,j] = subst_matrix[j,i]
  
        self.substitution_matrix = subst_matrix
  
      
        
    def needleman_wunsch (self):
       
        seq_1 = self.d_str_seq_1
        seq_2 = self.d_str_seq_2
        F = np.zeros((self._n_s1 + 1, self._n_s2 + 1))
        F[:,0] = np.linspace(0, 0, self._n_s1 + 1)
        F[0,:] = np.linspace(0, 0, self._n_s2 + 1)
       
        P = np.zeros((self._n_s1 + 1, self._n_s2 + 1))
        P[:,0] = 2
        P[0,:] = 3

        _temp = np.zeros(3)
        for i in range(self._n_s1):
            for j in range(self._n_s2):
                if seq_1[i] == seq_2[j]:
                    _temp[0] = F[i,j] + self.concordance_bonus
                    
                else:               
                    idx_1_y = ord(seq_1[i][0]) - 65
                    idx_1_x = ord(seq_1[i][1]) - 65
                    
                    idx_2_y = ord(seq_2[j][0]) - 65
                    idx_2_x = ord(seq_2[j][1]) - 65
                    
                    _idx_1 = idx_1_y*self.nb_loc_x + idx_1_x
                    _idx_2 = idx_2_y*self.nb_loc_x + idx_2_x
                    
                    _miss_value = self.substitution_matrix[_idx_1, _idx_2]
                    
                    _temp[0] = F[i,j] + _miss_value
                    #print(_miss_value)
                   
                _temp[1] = F[i,j+1] + self.gap_penalty
                _temp[2] = F[i+1,j] + self.gap_penalty
                tmax = np.max(_temp)
                F[i+1,j+1] = tmax
                if _temp[0] == tmax:
                    P[i+1,j+1] += 1
                elif _temp[1] == tmax:
                    P[i+1,j+1] += 2
                elif _temp[2] == tmax:
                    P[i+1,j+1] += 3
    
        i = self._n_s1
        j = self._n_s2
        r_s1 = []
        r_s2 = []
        
        score = F[i,j]
        normalized_score = score/(max(self._n_s1, self._n_s2) * self.concordance_bonus)
        print(max(self._n_s1, self._n_s2) * self.concordance_bonus)
        
        while i > 0 or j > 0:
            if P[i,j] == 1:
                r_s1.append(seq_1[i-1])
                r_s2.append(seq_2[j-1])
                i -= 1
                j -= 1
            elif P[i,j] == 2:
                r_s1.append(seq_1[i-1])
                r_s2.append('-')
                i -= 1
            elif P[i,j] == 3:
                r_s1.append('-')
                r_s2.append(seq_2[j-1])
                j -= 1
        # Reverse the strings.
        r_s1 = ','.join(r_s1)[::-1]
        r_s2 = ','.join(r_s2)[::-1]
        
        return '||'.join([r_s1, r_s2]), normalized_score


    
    def process (self):
        
        self.pre_process()
        self.compute_substitution_matrix()
        
        align, score = self.needleman_wunsch()

        self.result_set['scan_path_variables'].update({'scan_match': {}})
        self.result_set['scan_path_variables']['scan_match'].update({'alignement': align,
                                                                      'score': score})
        
        to_export = {'alignment score': score,
                     'horizontal box size': self.x_box_size,
                     'vertical box size': self.y_box_size,
                     'concordance bonus': self.concordance_bonus,
                     'gap penalty': self.gap_penalty}
        
        print('\n\n-----------------------------------------------------------------------')
        print("ScanMatch Analysis")
        print('-----------------------------------------------------------------------\n')
        
        for feature_name, value in to_export.items():
            print("\t{0:40}\t {1}".format(feature_name, np.round(value, 3)))
        
        print('\t')
        print('Sequence 1:')
        print(align.split('||')[0])
        print('\t')
        print('Sequence 2:')
        print(align.split('||')[1])
        
        if self.plot:
            self.plot_ScanMatch()
            
            
    def plot_ScanMatch (self):
        
   
        plt.style.use("seaborn")
        fig, axs = plt.subplots(1, 2, figsize=(12,6))
        fig.suptitle('Scan path 1')
        
        axs[0].scatter(self._sequence_1[:,0], 
                       self._sequence_1[:,1], 
                       color = 'cornflowerblue', s = 2.5)
        axs[0].set_title('Raw data')
        
        axs[1].scatter(self._loc_1[:,0], 
                       self._loc_1[:,1], 
                       color = 'cornflowerblue', s = 3.0)
        axs[1].set_title('bined data')

        for ax in axs.flat:
            ax.set(xlabel='Horizontal signal', ylabel='Vertical signal',)        
               
        #plt.savefig('simplification.png', bbox_inches='tight', dpi = 100)
        plt.show()
        plt.clf()
      
        fig, axs = plt.subplots(1, 2, figsize=(12,6))
        fig.suptitle('Scan path 2')
        
        axs[0].scatter(self._sequence_2[:,0], 
                       self._sequence_2[:,1], 
                       color = 'indianred', s = 2.5)
        axs[0].set_title('Raw data')
        
        axs[1].scatter(self._loc_2[:,0], 
                       self._loc_2[:,1], 
                       color = 'indianred', s = 3.0)
        axs[1].set_title('bined data')

        for ax in axs.flat:
            ax.set(xlabel='Horizontal signal', ylabel='Vertical signal',)        
        
         
        plt.show()
        plt.clf()


          
    def get_result_set (self):
        return self.result_set  
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
        