# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from numpy import linalg
from itertools import groupby
from operator import itemgetter
import copy

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx


class MultiMatch_Analysis():
    
    def __init__(self, 
                 data_set_1, data_set_2,  
                 amplitude_threshold, angular_threshold, 
                 duration_threshold, ratio_duration_length,
                 smoothed, plot):



        assert data_set_1['sampling_frequency'] == data_set_2['sampling_frequency'], 'Different sampling rates'
        assert data_set_1['size_plan_x'] == data_set_2['size_plan_x'], 'Different plan shapes'
        assert data_set_1['size_plan_y'] == data_set_2['size_plan_y'], 'Different plan shapes'
        
        
        self.delta_t = 1/data_set_1['sampling_frequency'] 
        self.plane_diag = np.sqrt(data_set_1['size_plan_x']**2 + data_set_1['size_plan_y']**2)
        
        self.data_set_1 = data_set_1
        self.data_set_2 = data_set_2
  
        self.plot = plot
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
        
        
        self._n_s1 = data_set_1['nb_samples']
        self._n_s2 = data_set_2['nb_samples']
        
        self._amp_thr = amplitude_threshold
        self._ang_thr = angular_threshold
        self._dur_thr = duration_threshold
        self._ratio_dur_length = ratio_duration_length
        
        self.initialize = True
        
        self._simplified_scan_path_1 = None
        self._simplified_scan_path_2 = None
        
        self._simplified_vec_1 = None
        self._simplified_vec_2 = None
        
        self._simplified_duration_vec_1 = None
        self._simplified_duration_vec_2 = None

        self._s_n_s1 = None
        self._s_n_s2 = None
        
        self._comparison_matrix = None
        
        self._aligned_sequence_1 = None
        self._aligned_sequence_2 = None
        
        
        
    def amplitude_based_clustering (self):
        
        if self.initialize == True:
            _planar_vec_1 = self._sequence_1[1:] - self._sequence_1[:self._n_s1-1]
            _planar_vec_2 = self._sequence_2[1:] - self._sequence_2[:self._n_s2-1]
            self.initialize = False
            
            _duration_vec_1 = np.ones(self._n_s1-1)*self.delta_t
            _duration_vec_2 = np.ones(self._n_s2-1)*self.delta_t
            
        else :
            _planar_vec_1 = self._simplified_vec_1
            _planar_vec_2 = self._simplified_vec_2 
            
            _duration_vec_1 = self._simplified_duration_vec_1
            _duration_vec_2 = self._simplified_duration_vec_2
            
            
        _norms_1 = linalg.norm(_planar_vec_1, axis = 1)
        _norms_2 = linalg.norm(_planar_vec_2, axis = 1)
        
        _is_low_1 = _norms_1 <= self._amp_thr
        _is_low_2 = _norms_2 <= self._amp_thr
        
        where_is_low_1 = np.where(_is_low_1 == True)[0]
        where_is_low_2 = np.where(_is_low_2 == True)[0]
        
        to_merge_intervals_1 = list()
        to_merge_intervals_2 = list()
        
        for k, g in groupby(enumerate(where_is_low_1), lambda ix : ix[0] - ix[1]):
            to_merge_interval_local = list(map(itemgetter(1), g))
            if to_merge_interval_local[0] != to_merge_interval_local[-1]:
                to_merge_ends_local = [to_merge_interval_local[0], to_merge_interval_local[-1]]
                to_merge_intervals_1.append(to_merge_ends_local)
                
        for k, g in groupby(enumerate(where_is_low_2), lambda ix : ix[0] - ix[1]):
            to_merge_interval_local = list(map(itemgetter(1), g))
            if to_merge_interval_local[0] != to_merge_interval_local[-1]:
                to_merge_ends_local = [to_merge_interval_local[0], to_merge_interval_local[-1]]
                to_merge_intervals_2.append(to_merge_ends_local) 

        
        to_remove_1 = []
        to_remove_2 = []
        
        _simplified_vec_1 = copy.deepcopy(_planar_vec_1)
        _simplified_vec_2 = copy.deepcopy(_planar_vec_2)
        
        for _int in to_merge_intervals_1:
            new_vec = np.zeros(2)
            new_duration = 0
            
            for i in list(np.linspace (_int[0], _int[-1], _int[-1]-_int[0] + 1)):
                new_vec += _planar_vec_1[int(i)]
                new_duration += 1
            
            _simplified_vec_1[_int[0]] = new_vec
            _duration_vec_1[_int[0]] = new_duration * self.delta_t
 
            to_remove_1.extend(list(np.linspace (_int[0]+1, _int[-1], _int[-1]-_int[0], dtype = np.int32)))
        
        _simplified_vec_1 = np.delete(_simplified_vec_1, to_remove_1, axis = 0)
        _duration_vec_1 = np.delete(_duration_vec_1, to_remove_1)
        
        
        for _int in to_merge_intervals_2:
            new_vec = np.zeros(2)
            new_duration = 0
            
            for i in list(np.linspace (_int[0], _int[-1], _int[-1]-_int[0] + 1)):
                new_vec += _planar_vec_2[int(i)]
                new_duration += 1
            
            _simplified_vec_2[_int[0]] = new_vec
            _duration_vec_2[_int[0]] = new_duration * self.delta_t
            
            to_remove_2.extend(list(np.linspace (_int[0]+1, _int[-1], _int[-1]-_int[0], dtype = np.int32)))    
        
        _simplified_vec_2 = np.delete(_simplified_vec_2, to_remove_2, axis = 0)
        _duration_vec_2 = np.delete(_duration_vec_2, to_remove_2)
       
        self._simplified_vec_1 = _simplified_vec_1
        self._simplified_vec_2 = _simplified_vec_2
        
        self._simplified_duration_vec_1 = _duration_vec_1
        self._simplified_duration_vec_2 = _duration_vec_2
        
        
    def angle_vecs (self, vec_a, vec_b):
        
        angle = np.arccos(np.matmul(vec_a, vec_b)/(np.linalg.norm(vec_a)*np.linalg.norm(vec_b)))
        return angle
    
    
    def direction_based_clustering (self):
        
        _simplified_vec_1 = copy.deepcopy(self._simplified_vec_1)
        _simplified_vec_2 = copy.deepcopy(self._simplified_vec_2)
        
        _simplified_duration_vec_1 = copy.deepcopy(self._simplified_duration_vec_1)
        _simplified_duration_vec_2 = copy.deepcopy(self._simplified_duration_vec_2)
        
        i = 1
        while i < len(_simplified_vec_1):
            vec_a = _simplified_vec_1[i-1]
            vec_b = _simplified_vec_1[i]
            angle = self.angle_vecs(vec_a, vec_b)* 180/np.pi
            ratio = _simplified_duration_vec_1[i]/linalg.norm(vec_b)
   
            if angle < self._ang_thr and ratio < self._ratio_dur_length and _simplified_duration_vec_1[i] < self._dur_thr:
                _simplified_vec_1[i-1] += _simplified_vec_1[i]
                _simplified_duration_vec_1[i-1] += self.delta_t 
                
                _simplified_vec_1 = np.delete(_simplified_vec_1, i, axis = 0)
                _simplified_duration_vec_1 = np.delete(_simplified_duration_vec_1, i)
            else :
                i += 1
        
        i = 1
        while i < len(_simplified_vec_2):
            vec_a = _simplified_vec_2[i-1]
            vec_b = _simplified_vec_2[i]
            angle = self.angle_vecs(vec_a, vec_b)* 180/np.pi
            ratio = _simplified_duration_vec_2[i]/linalg.norm(vec_b)
     
            if angle < self._ang_thr and ratio < self._ratio_dur_length and _simplified_duration_vec_2[i] < self._dur_thr:
                _simplified_vec_2[i-1] += _simplified_vec_2[i]
                _simplified_duration_vec_2[i-1] += self.delta_t
                
                _simplified_vec_2 = np.delete(_simplified_vec_2, i, axis = 0)
                _simplified_duration_vec_2 = np.delete(_simplified_duration_vec_2, i)
            else :
                i += 1
                
                
        _simplified_scan_path_1 = np.zeros((len(_simplified_vec_1)+1, 2))
        _simplified_scan_path_2 = np.zeros((len(_simplified_vec_2)+1, 2))
        
        _simplified_scan_path_1[0] = self._sequence_1[0]
        _simplified_scan_path_2[0] = self._sequence_2[0]
        
        for i in range (0, len(_simplified_vec_1)):
           _simplified_scan_path_1[i+1] = _simplified_scan_path_1[i] +  _simplified_vec_1[i]
        
        for i in range (0, len(_simplified_vec_2)):
           _simplified_scan_path_2[i+1] = _simplified_scan_path_2[i] +  _simplified_vec_2[i] 
           
        self._simplified_scan_path_1 = _simplified_scan_path_1  
        self._simplified_scan_path_2 = _simplified_scan_path_2  
        
        self._simplified_vec_1 = _simplified_vec_1
        self._simplified_vec_2 = _simplified_vec_2
        
        self._simplified_duration_vec_1 = _simplified_duration_vec_1
        self._simplified_duration_vec_2 = _simplified_duration_vec_2
        
        self._s_n_s1 = len(self._simplified_vec_1)
        self._s_n_s2 = len(self._simplified_vec_2)
  
  
  
    def compute_comparaison_matrix (self):
        
        comp_matrix = np.zeros((self._s_n_s1, self._s_n_s2))
        
        for i in range (0, self._s_n_s1):
            
            for j in range (0, self._s_n_s2):
                diff_vec = self._simplified_vec_1[i] - self._simplified_vec_2[j]   
                comp_matrix[i,j] = linalg.norm(diff_vec)
        
        self._comparison_matrix = comp_matrix

        
   
    def dijkstra_algorithm (self):
        
        adj_matrix = np.zeros((self._s_n_s1*self._s_n_s2, self._s_n_s1*self._s_n_s2)) 
        
        for i in range (0, self._s_n_s1 - 1):
            for j in range (0, self._s_n_s2 - 1):
                adj_matrix[i*self._s_n_s2 + j, i*self._s_n_s2 + j + 1] = self._comparison_matrix[i, j+1]
                adj_matrix[i*self._s_n_s2 + j, (i+1)*self._s_n_s2 + j] = self._comparison_matrix[i+1, j]
                adj_matrix[i*self._s_n_s2 + j, (i+1)*self._s_n_s2 + j + 1] = self._comparison_matrix[i+1, j+1]
        
        for i in range (0, self._s_n_s1 - 1):
            adj_matrix[i*self._s_n_s2 + self._s_n_s2 - 1, (i+1)*self._s_n_s2 + self._s_n_s2 - 1] = self._comparison_matrix[i+1, self._s_n_s2-1]
        
        for j in range (0, self._s_n_s2-1):
            adj_matrix[(self._s_n_s1 - 1)*self._s_n_s2 + j, (self._s_n_s1 - 1)*self._s_n_s2 + j+1] = self._comparison_matrix[self._s_n_s1 - 1, j+1]
      
        G = nx.from_numpy_matrix(adj_matrix, create_using=nx.DiGraph())
        _opt_path = nx.dijkstra_path(G, 0, self._s_n_s1*self._s_n_s2 - 1)
    
        results_1 = []
        results_2 = []
        
        for i, step in enumerate(_opt_path) :
            u = step//self._s_n_s2
            v = step%self._s_n_s2
            results_1.append(u)
            results_2.append(v)
        
        
        self._aligned_sequence_1 = np.array(results_1)
        self._aligned_sequence_2 = np.array(results_2)

        
        
    def compute_shape_diff (self):
        
        """
        Calculate vector similarity of two scanpaths.
        :return: _vector_diff: array of floats
                array of vector differences between pairs of saccades of two scanpaths
        """ 
    
        vector_diff = []
        
        for i in range (0, len(self._aligned_sequence_1)):

            vec_a = self._simplified_vec_1[self._aligned_sequence_1[i]]
            vec_b = self._simplified_vec_2[self._aligned_sequence_2[i]]
            
            vector_diff.append(linalg.norm(vec_a - vec_b))
            
        return np.array(vector_diff)/(2*self.plane_diag)
        
    
    def compute_position_diff (self):
        
        """
        Calculate position similarity of two scanpaths.
        :return: _pos_diff: array of floats
                array of position differences between pairs of saccades of two scanpaths
        """ 
        
        pos_diff = []
        
        for i in range (0, len(self._aligned_sequence_1)):
            
            fix_a = self._simplified_scan_path_1[self._aligned_sequence_1[i]]
            fix_b = self._simplified_scan_path_2[self._aligned_sequence_2[i]]
            
            pos_diff.append(linalg.norm(fix_b - fix_a))
        
        return np.array(pos_diff)/self.plane_diag
        
        
    def compute_angular_diff (self):
        
        """
        Calculate direction similarity of two scanpaths.
        :return: _angular_diff: array of floats
                array of vector differences between pairs of saccades of two scanpaths
        """ 
        
        angular_diff = []
        
        for i in range (0, len(self._aligned_sequence_1)):

            vec_a = self._simplified_vec_1[self._aligned_sequence_1[i]]
            vec_b = self._simplified_vec_2[self._aligned_sequence_2[i]]
            
            angular_diff.append(self.angle_vecs(vec_a, vec_b)* 180/np.pi)
            
        return np.array(angular_diff)/180
        
        
    def compute_length_diff (self):
        
        """
        Calculate length similarity of two scanpaths.
        :return: _len_diff: array of floats
                array of length difference between pairs of saccades of two scanpaths

        """ 
        
        len_diff = []
        
        for i in range (0, len(self._aligned_sequence_1)):

            vec_a = self._simplified_vec_1[self._aligned_sequence_1[i]]
            vec_b = self._simplified_vec_2[self._aligned_sequence_2[i]]
            
            len_diff.append(abs(linalg.norm(vec_a) - linalg.norm(vec_b)))
    
        return np.array(len_diff)/self.plane_diag
    
        
    def compute_duration_diff (self):
        
        """
        Calculate similarity of two scanpaths fixation durations.
        :return: _dur_diff: array of floats
                array of fixation duration differences between pairs of saccades from
        two scanpaths
        """ 
        
        dur_diff = []
        
        for i in range (0, len(self._aligned_sequence_1)):

            dur_a = self._simplified_duration_vec_1[self._aligned_sequence_1[i]]
            dur_b = self._simplified_duration_vec_2[self._aligned_sequence_2[i]]
            
            dur_diff.append(abs(dur_a - dur_b) / max(dur_a, dur_b))
    
        return np.array(dur_diff)
        
        
        
    def process (self):
        
        i = 0
        while i < 20:
            _old_len_1 = self._s_n_s1
            _old_len_2 = self._s_n_s2
       
            
            self.amplitude_based_clustering()
            self.direction_based_clustering()
            
            new_len_1 = self._s_n_s1
            new_len_2 = self._s_n_s2
            if new_len_1 == _old_len_1 and new_len_2 == _old_len_2:
                break
            i+=1
    
        self.compute_comparaison_matrix()      
        self.dijkstra_algorithm()
     
        results = [np.median(feature()) for feature in (self.compute_shape_diff,
                                                        self.compute_angular_diff,
                                                        self.compute_length_diff,
                                                        self.compute_position_diff,
                                                        self.compute_duration_diff)]
        
        self.result_set['scan_path_variables'].update({'multi_match': {}})
        self.result_set['scan_path_variables']['multi_match'].update({'shape': np.round(results[0],3),
                                                                      'angular': np.round(results[1],3),
                                                                      'length': np.round(results[2],3),
                                                                      'position': np.round(results[3],3),
                                                                      'duration': np.round(results[4],3)})

        to_export = self.result_set['scan_path_variables']['multi_match']
        print('\n\n-----------------------------------------------------------------------')
        print("MultiMatch Analysis")
        print('-----------------------------------------------------------------------\n')
        

        for feature_name, value in to_export.items():
            print("\t{0:40}\t {1}".format(feature_name + ' similarity', np.round(value, 3)))
        
        if self.plot:
            self.plot_scanpaths()
            
    def plot_scanpaths (self):
        
        plt.style.use("seaborn")
        fig, axs = plt.subplots(1, 2, figsize=(25,12))
        fig.suptitle('Scan path 1')
        
        axs[0].plot(self._sequence_1[:,0], 
                       self._sequence_1[:,1], 
                       linewidth = 0.5,)
        axs[0].set_title('Raw data')
        
        axs[1].plot(self._simplified_scan_path_1[:,0], 
                       self._simplified_scan_path_1[:,1], 
                       linewidth = 0.5)
        axs[1].set_title('Simplified data')


        for i in range (0, self._s_n_s1):
            dur = self._simplified_duration_vec_1[i]
            loc = self._simplified_scan_path_1[i]
          
            circle = plt.Circle((loc[0], loc[1]), dur*10, color='b')
            axs[1].add_patch(circle)
      
        for ax in axs.flat:
            ax.set(xlabel='Horizontal signal', ylabel='Vertical signal',)        
               
        #plt.savefig('simplification.png', bbox_inches='tight', dpi = 100)
        plt.show()
        plt.clf()
      

      
        fig, axs = plt.subplots(1, 2, figsize=(25,12))
        fig.suptitle('Scan path 2')
        
        axs[0].plot(self._sequence_2[:,0], 
                       self._sequence_2[:,1], 
                       linewidth = 0.5, color = 'indianred')
        axs[0].set_title('Raw data')
        
        axs[1].plot(self._simplified_scan_path_2[:,0], 
                       self._simplified_scan_path_2[:,1], 
                       linewidth = 0.5, color = 'indianred')
        axs[1].set_title('Simplified data')

        for i in range (0, self._s_n_s2):
            dur = self._simplified_duration_vec_2[i]
            loc = self._simplified_scan_path_2[i]
            
            circle = plt.Circle((loc[0], loc[1]), dur*10, color='red')
            axs[1].add_patch(circle)
            
        for ax in axs.flat:
            ax.set(xlabel='Horizontal signal', ylabel='Vertical signal',)        
        
         
        plt.show()
        plt.clf()
  
        
    def get_result_set (self):
        return self.result_set   
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
        