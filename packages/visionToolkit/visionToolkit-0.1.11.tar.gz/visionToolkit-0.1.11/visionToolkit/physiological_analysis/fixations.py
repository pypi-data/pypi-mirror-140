

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter


class Fixations_Analysis():
    
    def __init__(self, data_set, 
                 method, fix_threshold, sac_threshold, 
                 duration_threshold, dispersion_threshold, angular_distance_threshold,
                 smoothed, plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set
        
        self.method = method
        
        self.smoothed = smoothed
        self.plot = plot
        
        self.fix_threshold = fix_threshold
        self.sac_threshold = sac_threshold 
        self.duration_threshold = duration_threshold 
        self.dispersion_threshold = dispersion_threshold 
        self.angular_distance_threshold = angular_distance_threshold
            
        self.result_set = {'physiological_variables': {}}
        self.dict_methods = {'I_VT': self.process_IVT,
                             'I_DiT': self.process_IDiT,
                             'I_DeT': self.process_IDeT}


    def centroid(self, x_coords, y_coords):

        _len = len(x_coords)
        centroid_x = sum(x_coords)/_len
        centroid_y = sum(y_coords)/_len
        return [centroid_x, centroid_y]
    
    
    #Velocity based
    def process_IVT (self, data_set):
        
        if self.smoothed:
            absolute_speed_deg = data_set['smoothed_absolute_speed_deg']
            x_coords = data_set['smoothed_x_array']
            y_coords = data_set['smoothed_y_array']
        else:
            absolute_speed_deg = data_set['absolute_speed_deg']
            x_coords = data_set['x_array']
            y_coords = data_set['y_array']
            
        is_fixation = absolute_speed_deg <= self.fix_threshold
        where_is_fixation = np.where(is_fixation == True)[0]
        fixation_intervals = list()
        centroids = list()
        
        for k, g in groupby(enumerate(where_is_fixation), lambda ix : ix[0] - ix[1]):
            fixation_interval_local = list(map(itemgetter(1), g))
            fixation_ends_local = [fixation_interval_local[0], fixation_interval_local[-1]]
            fixation_intervals.append(fixation_ends_local)
            centroids.append(self.centroid(x_coords[fixation_interval_local[0]: fixation_interval_local[-1]+1], 
                                           y_coords[fixation_interval_local[0]: fixation_interval_local[-1]+1]))
      
        results = {'is_fixation': is_fixation,
                   'fixation_intervals': fixation_intervals,
                   'centroids': centroids}
        return results
        
    
    #Dispersion based
    def process_IDiT (self, data_set):
        
        if self.smoothed:
            x_coords = data_set['smoothed_x_array']
            y_coords = data_set['smoothed_y_array']
        else:
            x_coords = data_set['x_array']
            y_coords = data_set['y_array']
            
        sampling = self.data_set['sampling_frequency']
        duration_threshold = int((self.duration_threshold * 1e-3*sampling) + 1)
        dispersion_threshold = self.dispersion_threshold
        
        is_fixation = np.zeros(self.nb_samples)
        fixation_intervals = list()
        centroids = list()
        
        i = 0
        while i+duration_threshold < self.nb_samples :
            j = i+duration_threshold
            d = self.dispersion_metric(x_coords[i:j], y_coords[i:j])
            if d < dispersion_threshold :
                local_interval = [i]
                while d < dispersion_threshold and j < self.nb_samples-1:
                    j+=1
                    d = self.dispersion_metric(x_coords[i:j], y_coords[i:j])       

                local_interval.append(j-1)
                fixation_intervals.append(local_interval)
                centroids.append(self.centroid(x_coords[local_interval[0]: local_interval[1]+1], 
                                               y_coords[local_interval[0]: local_interval[1]+1]))
                is_fixation[i:j] = 1.0
                i = j                
                
            else:
                i += 1
           
        is_fixation = is_fixation == 1.0
        results = {'is_fixation': is_fixation,
                   'fixation_intervals': fixation_intervals,
                   'centroids': centroids}
        return results
    
    
    def dispersion_metric (self, x_coords, y_coords):
        
        d = np.sqrt((np.max(x_coords) - np.min(x_coords))**2 + (np.max(y_coords) - np.min(y_coords))**2)
        return d  
      
    
    #Modified DBSCAN - Density based
    def process_IDeT (self, data_set):
        
        if self.smoothed:
            unitary_gaze_vectors = data_set['smoothed_unitary_gaze_vectors']
        else:
            unitary_gaze_vectors = data_set['unitary_gaze_vectors']
            
        vareps = self.angular_distance_threshold
        
        min_pts = int(self.duration_threshold
                      *self.data_set['sampling_frequency']/1000) + 1
                    
        available = {i: True for i in range(0, self.nb_samples)}
        C_clusters = []
        for i in range (0, self.nb_samples):
       
            if available[i] == True:
                neighborhood = self.vareps_neighborhood(unitary_gaze_vectors, i, vareps)      
                if len(neighborhood)+1 >= min_pts: 
                           
                    available[i] = False
                    local_C_cluster, available = self.expand_cluster (unitary_gaze_vectors, i, neighborhood, vareps, min_pts, available)
    
                    if len(local_C_cluster) >= min_pts:
                        C_clusters.append(local_C_cluster)

        fixation_intervals = list()
        is_fixation = np.zeros(self.nb_samples)
        
        for clust in C_clusters:
            local_fix = list()
            local_fix.append(min(clust))
            local_fix.append(max(clust))
            fixation_intervals.append(local_fix)
            is_fixation[local_fix[0]: local_fix[-1]+1] = 1
   
      
        results = {'is_fixation': is_fixation,
                   'fixation_intervals': fixation_intervals,
                   'centroids': None}
        return results
        
    
    def absolute_angular_distance(self, gaze_vect_1, gaze_vect_2):
        
        absolute_angular_distance_rad = np.arccos(np.round(np.matmul(gaze_vect_1, gaze_vect_2) ,8))
        absolute_angular_distance_deg = np.abs(absolute_angular_distance_rad/(2*np.pi)*360)
        
        return absolute_angular_distance_deg
    
    
    def vareps_neighborhood (self, unitary_gaze_vectors, idx, vareps):
    
        neighborhood = []
        ref_gaze_vector = unitary_gaze_vectors[:,idx]
    
        #a gauche
        d_l = 0
        l = idx
        while l > 0 and d_l < vareps:
            l -= 1
            d_l = self.absolute_angular_distance(ref_gaze_vector, unitary_gaze_vectors[:,l])
        neighborhood += [i for i in range(l+1, idx)]
    
        #a droite
        d_r = 0
        r = idx
        while r+1 < self.nb_samples and d_r < vareps:
            r += 1
            d_r = self.absolute_angular_distance(ref_gaze_vector, unitary_gaze_vectors[:,r])
        neighborhood += [i for i in range(idx+1, r)]
        neighborhood = sorted(neighborhood)
    
        return neighborhood
    
    
    def expand_cluster (self, unitary_gaze_vectors, idx, neighborhood, vareps, min_pts, available):
        
        local_C_cluster = [idx]
        for neigh_idx in neighborhood:
    
            new_neighborhood = self.vareps_neighborhood (unitary_gaze_vectors, neigh_idx, vareps)       
            if len(new_neighborhood)+1 >= min_pts:
                
                for key in new_neighborhood :
                    if key not in neighborhood:
                        neighborhood.append(key)
       
                if available[neigh_idx] == True:
                    
                    local_C_cluster.append(neigh_idx)
                    available[neigh_idx] = False
                
        return local_C_cluster, available
    
    
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
            
        nb_fixations = len(results['fixation_intervals'])
        length = 0
        amplitude = 0
        
        for fix_int in results['fixation_intervals']:
            length += fix_int[-1] + 1 - fix_int[0] 
        
        mean_length = (length * 1000)/(nb_fixations * self.data_set['sampling_frequency'])
        
        duration = self.nb_samples/self.data_set['sampling_frequency']
        frequency = nb_fixations/duration

        basic_features.update({'method:': self.method,
                               'number of fixations:': nb_fixations,
                               'fixation mean duration (ms):': mean_length,
                               'fixation frequency (/s)': frequency})
        return basic_features
    
    
    def process (self):

        results = self.dict_methods[self.method](self.data_set)   
        basic_features = self.basic_features(results)
        
        self.result_set['physiological_variables']['fixations'] = {}
        self.result_set['physiological_variables']['fixations'].update({'method': self.method,
                                                                         'is_fixation': results['is_fixation'],
                                                                         'fixation_intervals': results['fixation_intervals'],
                                                                         'centroids': results['centroids']})  
        
        print('\n\n-----------------------------------------------------------------------')
        print("Basic features for fixation analysis")
        print('-----------------------------------------------------------------------\n')

        for feature_name, value in basic_features.items():
            if type(value) == str:
                print("\t{0:40}\t {1}".format(feature_name, value))
            else:
                print("\t{0:40}\t {1}".format(feature_name, round(value,3)))
        
        if self.plot:
            self.plot_fixations(results['fixation_intervals'])
    
    
    def get_result_set (self):
        return self.result_set
        
        
    def plot_fixations (self, fixation_intervals):
        
        if self.smoothed:
            x_coords = self.data_set['smoothed_x_array']
            y_coords = self.data_set['smoothed_y_array']
        else:
            x_coords = self.data_set['x_array']
            y_coords = self.data_set['y_array']
         
        plt.style.use("seaborn")
        x = 1000*np.array(np.arange(0, self.nb_samples))/self.data_set['sampling_frequency']       
        plt.plot(x, x_coords, linewidth = 0.2, color = 'black')
        for fix_int in fixation_intervals:
          
            x = 1000*np.array(np.arange(fix_int[0], fix_int[-1]+1))/self.data_set['sampling_frequency']
            y = x_coords[fix_int[0]: fix_int[-1]+1] 
            plt.plot(x, y, color = 'cornflowerblue')
            
        plt.xlabel("Time (ms)", fontsize =9)
        plt.ylabel("Horizontal position (px)", fontsize =9) 
        
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)  
        
        plt.show()
        plt.clf()
        
        x = 1000*np.array(np.arange(0, self.nb_samples))/self.data_set['sampling_frequency']
        plt.plot(x, y_coords, linewidth = 0.2, color = 'black')
        for fix_int in fixation_intervals:
        
            x = 1000*np.array(np.arange(fix_int[0], fix_int[-1]+1))/self.data_set['sampling_frequency']
            y = y_coords[fix_int[0]: fix_int[-1]+1] 
            plt.plot(x, y, color = 'cornflowerblue')
            
        plt.xlabel("Time (ms)", fontsize =9)
        plt.ylabel("Horizontal position (px)", fontsize =9) 
        
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7) 
        
        plt.show()
        plt.clf()    
        
        for fix_int in fixation_intervals:
          
            x = x_coords[fix_int[0]: fix_int[-1]+1]
            y = y_coords[fix_int[0]: fix_int[-1]+1] 
            plt.plot(x, y, color = 'cornflowerblue', linewidth = 0.5)   
            
        plt.xlabel("Horizontal position (px)", fontsize =9)
        plt.ylabel("Vertical position (px)", fontsize =9) 
        
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
        
        plt.show()
        plt.clf()    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        