

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


class MSD_Analysis():
    
    def __init__(self, 
                 data_set, 
                 min_lag, max_lag, nb_lags,
                 smoothed, plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set
        
        self.smoothed = smoothed
        self.plot = plot
        
        self.min_lag = min_lag
        self.max_lag = max_lag
        self.nb_lags = nb_lags
        
        self.result_set = {'statistical_variables': {}}
          
        
    def MSD (self, x, lag):
        
        msd = 0
        
        for i in range (2, self.nb_samples - lag-2):
            msd += (x[i+lag] - x[i])**2
        msd = msd/(self.nb_samples - lag)   
        
        return msd


    def generate_MSDs (self, x, y):
        
        log_mini = np.round(np.log10(self.min_lag))
        log_maxi = np.round(np.log10(self.max_lag))
        
        log_lags = np.linspace(log_mini, log_maxi, self.nb_lags)
        lags = np.round(10**log_lags)
        new_lags = (list(set(lags)))
        new_lags.sort()
        lags_MSD = new_lags
        nb_lags = len(new_lags)
      
        MSDs = np.zeros((2, nb_lags))
        
        for count, lag in enumerate(new_lags):
            MSDs[0,count] = self.MSD(x, int(lag))
            MSDs[1,count] = self.MSD(y, int(lag))        
            
        return lags_MSD, MSDs
    
    
    def process (self):
        
        if self.smoothed:
            x_arr = self.data_set['smoothed_x_array']
            y_arr = self.data_set['smoothed_y_array']
        else :
            x_arr = self.data_set['x_array']
            y_arr = self.data_set['y_array']   
            
        lags, MSDs = self.generate_MSDs(x_arr,
                                        y_arr)   
        
        self.result_set['statistical_variables']['stochastic'] = {'MSD': {}}
        self.result_set['statistical_variables']['stochastic']['MSD'] = ({'lags': lags,
                                                                           'MSDs': MSDs})
        print("  MSDs generated")
        
        if self.plot:
            self.plot_MSD(lags, 
                          MSDs)
        
        
    def plot_MSD (self, 
                  lags_MSD, 
                  MSDs, 
                  direction = 'both'):
        
        plt.style.use("seaborn")
        lg_msd = np.log10(MSDs)     
        lg_lag = np.log10(lags_MSD)
        
        fig = plt.figure(figsize=(8,6))
        if direction == 'x':
            plt.plot(lg_lag, lg_msd[0,:], linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
        elif direction == 'y':
            plt.plot(lg_lag, lg_msd[1,:], linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
        else :
            plt.plot(lg_lag, lg_msd[0,:], linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
            plt.plot(lg_lag, lg_msd[1,:], linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
              
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
    
        plt.xlabel("log-lag", fontsize =9)
        plt.ylabel("log-MSD", fontsize =9) 
        plt.legend(fontsize = 9)
        
        plt.show()
        plt.clf()


    def get_result_set (self):
        return self.result_set
        
    
    
    