

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


class DACF_Analysis():
    
    def __init__(self, 
                 data_set, 
                 min_lag, max_lag, nb_lags, order,
                 smoothed, plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set
        
        self.smoothed = smoothed
        self.plot = plot
        
        self.min_lag = min_lag
        self.max_lag = max_lag
        self.nb_lags = nb_lags
        self.order = order
        
        self.result_set = {'statistical_variables': {}}
       
        
    def DACF (self, x, lag) :
            
        DACF = 0
        
        for i in range (0, self.nb_samples - lag - self.order):
            DACF += (1/self.order**2)*((x[i+lag+self.order]-x[i+lag])*(x[i+self.order]-x[i]))
        DACF = DACF/(self.nb_samples-lag-self.order)   
        
        return DACF


    def generate_DACFs (self, x, y):
        
        lags = np.linspace(self.min_lag, self.max_lag, self.nb_lags)
        lags_DACF = lags
        
        DACFs = np.zeros((2, self.nb_lags))
        normalized_DACFs = np.zeros((2, self.nb_lags))
        for count, lag in enumerate(lags):
            DACFs[0,count] = self.DACF(x, int(lag))
            DACFs[1,count] = self.DACF(y, int(lag))
        
        normal_x = DACFs[0,0]
        normal_y = DACFs[1,0]  
        
        normalized_DACFs[0,:] = DACFs[0,:]/normal_x
        normalized_DACFs[1,:] = DACFs[1,:]/normal_y 
        
        return lags_DACF, normalized_DACFs
    
    
    def process (self):
        
        if self.smoothed:
            x_arr = self.data_set['smoothed_x_array']
            y_arr = self.data_set['smoothed_y_array']
        else :
            x_arr = self.data_set['x_array']
            y_arr = self.data_set['y_array']   
           
        lags, DACFs = self.generate_DACFs(x_arr,
                                          y_arr)   
        
        self.result_set['statistical_variables']['stochastic'] = {'DACF': {}}    
        self.result_set['statistical_variables']['stochastic']['DACF'] = ({'lags': lags,
                                                                           'DACFs': DACFs})
        print("  DACFs generated")
        
        if self.plot:
            self.plot_DACF(lags, 
                           DACFs)
        
        
    def plot_DACF (self, 
                   lags_DACF, 
                   DACFs, 
                   direction = 'both'):
        
        plt.style.use("seaborn")
        fig = plt.figure(figsize=(8,6))
        if direction == 'x':
            plt.plot(lags_DACF, DACFs[0,:], linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
        elif direction == 'y':
            plt.plot(lags_DACF, DACFs[1,:], linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
        else :
            plt.plot(lags_DACF, DACFs[0,:], linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
            plt.plot(lags_DACF, DACFs[1,:], linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
              
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
    
        plt.xlabel("lag", fontsize =9)
        plt.ylabel("DACF of order {k}".format(k = self.order), fontsize =9) 
        plt.legend(fontsize = 9)
        
        plt.show()
        plt.clf()

    def get_result_set (self):
        return self.result_set