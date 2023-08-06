# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import math 

from scipy.stats import f
from sklearn.decomposition import PCA

from .utilities import confidence_ellipse

class Dispersion():

    def __init__(self,
                 data_set,
                 smoothed,
                 plot):
    
        self.data_set = data_set
        self.nb_samples = data_set['nb_samples']
        self.delta_t = 1/data_set['sampling_frequency']
        

        self.result_set = {'statistical_variables': {}}
        self.smoothed=smoothed
        self.plot = plot

    def process(self):

        self.centered_x_array, self.centered_y_array = self.generate_centered_trajectories()
        
        radius_signal = self.generate_radius_signal()
        cov = self.compute_covariance()
        mean_x, mean_y = self.compute_average()
        mean_dist_centered_x, mean_dist_centered_y, mean_dist_radius_signal = self.compute_distance()
        max_centered_x, max_centered_y, max_radius = self.compute_maximum()
        rms_centered_x, rms_centered_y, rms_radius = self.compute_RMS()
        range_x, range_y, range_xy  = self.compute_ranges()
        range_ratio = self.compute_range_ratio()
        planar_deviation = self.compute_planar_deviation()
        coeff_sway_direction = self.compute_sway_direction()
        confidence_sway_area = self.compute_confidence_sway_area()
        principal_sway_direction = self.compute_principal_sway_direction()

        self.result_set['statistical_variables']['position'] = {'centered_x_array': self.centered_x_array,
                                                                'centered_y_array': self.centered_y_array,
                                                                'radius_signal': radius_signal,
                                                                'cov': cov,
                                                                'mean_x': mean_x,
                                                                'mean_y': mean_y,
                                                                'mean_dist_centered_x': mean_dist_centered_x,
                                                                'mean_dist_centered_y': mean_dist_centered_y,
                                                                'mean_dist_radius_signal': mean_dist_radius_signal,
                                                                'max_centered_x': max_centered_x,
                                                                'max_centered_y': max_centered_y,
                                                                'max_radius': max_radius,
                                                                'rms_centered_x': rms_centered_x,
                                                                'rms_centered_y': rms_centered_y,
                                                                'rms_radius': rms_radius,
                                                                'range_x': range_x,
                                                                'range_y': range_y,
                                                                'range_xy': range_xy,
                                                                'range_ratio': range_ratio,
                                                                'planar_deviation': planar_deviation,
                                                                'coeff_sway_direction': coeff_sway_direction,
                                                                'confidence_sway_area': confidence_sway_area,
                                                                'principal_sway_direction': principal_sway_direction}
        if self.plot:
            self.plot_scatter_trajectory()
            self.plot_trajectories()
            self.summary()

    def get_result_set (self):
        return self.result_set


    def generate_centered_trajectories (self):
    
        if self.smoothed:
            centered_x_array = self.data_set['smoothed_x_array']-self.data_set['smoothed_x_array'].mean()
            centered_y_array = self.data_set['smoothed_y_array']-self.data_set['smoothed_y_array'].mean()
        else:
            centered_x_array = self.data_set['x_array']-self.data_set['x_array'].mean()
            centered_y_array = self.data_set['y_array']-self.data_set['y_array'].mean()

        return centered_x_array, centered_y_array

    def generate_radius_signal (self):
    
        radius_signal = np.sqrt(self.centered_x_array**2 + self.centered_y_array**2)
        return radius_signal

    def compute_covariance (self):

        cov = (1/self.nb_samples)*(self.centered_x_array*self.centered_y_array).sum()
        return cov

    def compute_average (self):
    
        if self.smoothed:
            mean_x = self.data_set['smoothed_x_array'].mean()
            mean_y = self.data_set['smoothed_y_array'].mean()
        else:
            mean_x = self.data_set['x_array'].mean()
            mean_y = self.data_set['y_array'].mean()
        return mean_x, mean_y    

    def compute_distance (self):
    
        radius_signal = self.generate_radius_signal()

        mean_dist_centered_x = np.abs(self.centered_x_array).mean()
        mean_dist_centered_y = np.abs(self.centered_y_array).mean()
        mean_dist_radius_signal = np.abs(radius_signal).mean()

        return mean_dist_centered_x, mean_dist_centered_y, mean_dist_radius_signal


    def compute_maximum (self):

        radius_signal = self.generate_radius_signal()

        max_centered_x = np.abs(self.centered_x_array).max()
        max_centered_y = np.abs(self.centered_y_array).max()
        max_radius = radius_signal.max()
        return max_centered_x, max_centered_y, max_radius   

    def compute_RMS (self):

        radius_signal = self.generate_radius_signal()

        rms_centered_x = np.sqrt((1/self.nb_samples)*(self.centered_x_array**2).sum())
        rms_centered_y = np.sqrt((1/self.nb_samples)*(self.centered_y_array**2).sum())
        rms_radius = np.sqrt((1/self.nb_samples)*(radius_signal**2).sum())
        return rms_centered_x, rms_centered_y, rms_radius

    def compute_ranges (self):
    
        range_x = self.centered_x_array.max() - self.centered_x_array.min()
        range_y = self.centered_y_array.max() - self.centered_y_array.min()
        range_xy = np.sqrt(np.max([(self.centered_x_array[i]-self.centered_x_array[j])**2 + (self.centered_y_array[i]-self.centered_y_array[j])**2
                                    for i in range(self.nb_samples) for j in range(i, self.nb_samples)]))
        return range_x, range_y, range_xy

    def compute_range_ratio (self):

        range_x, range_y, _ = self.compute_ranges()
        range_ratio = range_x/range_y

        return range_ratio
    
    def compute_planar_deviation (self):

        rms_centered_x, rms_centered_y, _ = self.compute_RMS()
        planar_deviation = np.sqrt( rms_centered_x**2 + rms_centered_y**2)
        return planar_deviation

    def compute_sway_direction (self):

        rms_centered_x, rms_centered_y, _ = self.compute_RMS()
        cov = self.compute_covariance()

        coeff_sway_direction = cov/(rms_centered_x*rms_centered_y)
        return coeff_sway_direction

    def compute_confidence_sway_area (self):

        rms_centered_x, rms_centered_y, _ = self.compute_RMS()
        cov = self.compute_covariance()  

        confidence_sway_area = 2*np.pi*(self.nb_samples-1)/(self.nb_samples-2)*f.ppf(.95, 2, self.nb_samples-2)*np.sqrt(rms_centered_x**2*rms_centered_y**2- cov**2)     
        return confidence_sway_area
    
    def compute_principal_sway_direction (self):

        pca = PCA(n_components=2)
        X = np.concatenate([self.centered_x_array[:, np.newaxis], self.centered_y_array[:, np.newaxis]], axis=1)
        pca.fit(X)
        v1, v2 = pca.components_[0]

        principal_sway_direction = math.acos(np.abs(v2)/np.sqrt(v1**2+v2**2))*(180/np.pi)
        return principal_sway_direction


    def summary(self):
            
        print('\n\n-----------------------------------------------------------------------')
        print("Variables for the gaze trajectory (smoothed={})".format(self.smoothed))
        print('-----------------------------------------------------------------------\n')

        for feature_name, value in self.result_set['statistical_variables']['position'].items():
            if feature_name not in ['centered_x_array', 'centered_y_array', 'radius_signal']:
                print("\t{0:40}\t {1}".format(feature_name, round(value,3)))


    def plot_trajectories(self):

        time = np.linspace(0, self.nb_samples*self.delta_t, self.nb_samples)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(25, 8))

        ax1.plot(time, 
                self.result_set['statistical_variables']['position']['centered_x_array'], 
                color='b',
                label='signal (smoothed={})'.format(self.smoothed))
        ax1.set_title("Evolution of the centered X trajectory", fontsize=18, weight='bold')
        ax1.set_ylabel("X-coordinate", fontsize=18)
        ax1.set_xlabel("Time [s]", fontsize=18)
        ax1.set_xticks(np.linspace(0, self.nb_samples*self.delta_t, 8).round())
        ax1.set_xticklabels(np.linspace(0, self.nb_samples*self.delta_t, 8).round())
        ax1.legend()

        ax2.plot(time, 
                self.result_set['statistical_variables']['position']['centered_y_array'], 
                color='b',
                label='signal (smoothed={})'.format(self.smoothed))
        ax2.set_title("Evolution of the centered Y trajectory", fontsize=18, weight='bold')
        ax2.set_ylabel("Y-coordinate", fontsize=18)
        ax2.set_xlabel("Time [s]", fontsize=18)
        ax2.set_xticks(np.linspace(0, self.nb_samples*self.delta_t, 8).round())
        ax2.set_xticklabels(np.linspace(0, self.nb_samples*self.delta_t, 8).round())
        ax2.legend()
        plt.tight_layout()
        plt.show()
        return

    def plot_scatter_trajectory(self):
        
        time = np.linspace(0, self.nb_samples*self.delta_t, self.nb_samples)
        x = self.result_set['statistical_variables']['position']['centered_x_array']
        y = self.result_set['statistical_variables']['position']['centered_y_array']

        fig, ax = plt.subplots(1, 1, figsize=(12, 12))

        ax.scatter(x, y, color='b', s=.8, label='Signal (smoothed={})'.format(self.smoothed))
        
        rotation = self.result_set['statistical_variables']['position']['principal_sway_direction']
        confidence_ellipse(x,y, ax, rotation=rotation, n_std=1, edgecolor='firebrick', label=r'$1\sigma$')
        confidence_ellipse(x,y, ax, rotation=rotation,  n_std=2, edgecolor='fuchsia', label=r'$2\sigma$')
        confidence_ellipse(x,y, ax, rotation=rotation,  n_std=3, edgecolor='blue', label=r'$3\sigma$')
        ax.axline((0,0), 
                  slope=np.sin((rotation+90)*np.pi/180)/np.cos((rotation+90)*np.pi/180),
                  linestyle='--',
                  color='grey', 
                  label='Sway Direction')

        ax.set_title("Scatter plot of the trajectory", fontsize=18, weight='bold')
        ax.set_xlabel("X-coordinate", fontsize=18),ax.set_ylabel("Y-coordinate", fontsize=18)

        ax.legend()
        plt.show()
        return
        
        
        
        
        
        
        
        