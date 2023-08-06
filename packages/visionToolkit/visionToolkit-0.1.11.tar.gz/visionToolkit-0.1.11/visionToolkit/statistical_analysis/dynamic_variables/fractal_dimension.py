# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances

import matplotlib.pyplot as plt
from hilbertcurve.hilbertcurve import HilbertCurve



class Fractal_Analysis():
    
    def __init__(self, 
                 data_set, 
                 method, hilbert_iterations, k_max, nb_box, fill_factor,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set
        
        self.hilbert_iterations = hilbert_iterations
        self.k_max = k_max
        self.nb_box = nb_box
        self.fill_factor = fill_factor
        
        self.result_set = {'statistical_variables': {}}
        self.plot = plot
        
        self.method = method
        self.dict_methods = {'H_FD': self.process_HFD,
                             'MB_FD': self.process_MBFD}
        
        self.fractal_dimension = None
        
        
        
    def hilbert_distance (self, locations):
        
        hilbert_curve = HilbertCurve(self.hilbert_iterations, 2)
        distances = hilbert_curve.distances_from_points(locations)
        
        return distances
    
    
        
    def Higuchi_FD (self, input_val):
        
        L = list()
        x = list()
        N = len(input_val)
        
        for k in range(1, self.k_max):
            Lk = 0
            for m in range(0, k):
      
                idxs = np.arange(1,int(np.floor((N-m)/k)),dtype=np.int32)
                  
                Lmk = np.sum(np.abs(input_val[m + idxs*k] - input_val[m + k*(idxs - 1)]))
                Lmk = (Lmk*(N - 1)/(((N - m)/ k)* k**2)) 
                Lk += Lmk
        
            L.append(np.log(Lk / (m + 1)))
            x.append(np.log(1.0 / k))
          
        slope = np.polyfit(x, L, 1)
       
        return slope[0]
    
    
    
    def process_HFD (self):
        
        nb_axis_loc = self.hilbert_iterations**2 
        
        x_box_size = self.data_set['size_plan_x']/nb_axis_loc
        y_box_size = self.data_set['size_plan_y']/nb_axis_loc
        
        x_coords = self.data_set['smoothed_x_array']
        y_coords = self.data_set['smoothed_y_array']
        
        locations = np.zeros((self.nb_samples, 2), dtype = np.int32)
        locations[:,0] = (x_coords*(1/x_box_size)).astype(int)
        locations[:,1] = (y_coords*(1/y_box_size)).astype(int)
        
        distances = self.hilbert_distance(locations)
        self.fractal_dimension = self.Higuchi_FD(np.array(distances)) 
        
        to_export = {'Higuchi fractal_dimension': self.fractal_dimension,
                     'number of hilbert iterations': self.hilbert_iterations,
                     'Higuchi k max:': self.k_max}
        
        print('\n\n-----------------------------------------------------------------------')
        print("Higuchi Fractal Analysis")
        print('-----------------------------------------------------------------------\n')

        for feature_name, value in to_export.items():
            if type(value) == str:
                print("\t{0:40}\t {1}".format(feature_name, value))
            else:
                print("\t{0:40}\t {1}".format(feature_name, round(value,3)))
               
        if self.plot:

            self.plot_HFD(locations, distances)
        

        


    def plot_HFD (self, 
                  locations, distances):
        
        plt.style.use("seaborn")
        
        hilbert_curve = HilbertCurve(self.hilbert_iterations, 2)
        distances_plot = list(range(min(distances), max(distances)+1))
        points = hilbert_curve.points_from_distances(distances_plot)
        points = np.array(points)
        
        plt.plot(points[:,0], points[:,1], linewidth = 0.2)
        
        plt.plot(locations[:,0], locations[:,1], linestyle="",marker="o", markersize = 3.0, color = 'indianred')
        
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
        
        plt.xlim((min(locations[:,0]), max(locations[:,0])))
        plt.ylim((min(locations[:,1]), max(locations[:,1])))
    
        plt.xlabel("Horizontal position", fontsize =9)
        plt.ylabel("Vertical position", fontsize =9) 
        
        plt.show()
        plt.clf()
        
        
        
    def process_MBFD (self):
        
        nb_axis_box = self.nb_box
        
        x_box_size = self.data_set['size_plan_x']/nb_axis_box
        y_box_size = self.data_set['size_plan_y']/nb_axis_box
        
        x_coords = self.data_set['smoothed_x_array']
        y_coords = self.data_set['smoothed_y_array']
        
        locations = np.zeros((self.nb_samples, 2), dtype = np.int32)
        locations[:,0] = (x_coords*(1/x_box_size)).astype(int)
        locations[:,1] = (y_coords*(1/y_box_size)).astype(int)
        
        fill_factor = self.fill_factor
        
        test_x = x_coords
        test_y = y_coords
  
        val_x = [test_x[0]] + [np.nan]*(fill_factor-1)
        val_y = [test_y[0]] + [np.nan]*(fill_factor-1)
        
        for i in range (1, len(test_x)):
            val_x += [test_x[i]] + [np.nan]*(fill_factor-1)
            val_y += [test_y[i]] + [np.nan]*(fill_factor-1)
        
        val = np.concatenate((np.array(val_x).reshape(fill_factor*self.nb_samples,1),
                              np.array(val_y).reshape(fill_factor*self.nb_samples,1)), axis = 1)
            
        idx = list(np.linspace(0, (fill_factor-1), fill_factor))
        
        for i in range (1, len(test_x)):
            idx += list(np.linspace(fill_factor*i, fill_factor*i + (fill_factor-1), fill_factor))    
        
        df = pd.DataFrame(val, index=idx)
        df_f = df.interpolate(method='linear')
        
        locations = np.zeros((self.nb_samples*fill_factor, 2), dtype = np.int32)
        
        locations[:,0] = (df_f.iloc[:,0].to_numpy()*(1/x_box_size)).astype(int)
        locations[:,1] = (df_f.iloc[:,1].to_numpy()*(1/y_box_size)).astype(int) 
      
        plt.plot(locations[:,0], locations[:,1], linestyle="",marker=".")
    
        
        
    def process (self):
        
        self.dict_methods[self.method]()
        
        self.result_set['statistical_variables']['dynamic'] = {'fractal_dimension': {}}
        self.result_set['statistical_variables']['dynamic']['fractal_dimension'] = ({'method': self.method,
                                                                                     'fractal_dimension': self.fractal_dimension})


        
    def get_result_set (self):
        return self.result_set    
        
        
        
        
        
        
        
        
        