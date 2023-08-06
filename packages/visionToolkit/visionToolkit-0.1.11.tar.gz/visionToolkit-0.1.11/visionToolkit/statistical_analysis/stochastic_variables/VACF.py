

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


class VACF_Analysis():
    
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
          
    
    def VACF (self, v, lag) :
            
        VACF = 0
        
        for i in range (0, len(v)-lag):
            VACF += v[i+lag]*v[i]
        VACF = VACF*(1/(len(v)-lag))
        
        return VACF

    
    def generate_VACFs (self, speed_vectors):
        
        lags = np.linspace(self.min_lag, self.max_lag, self.nb_lags)
        lags_VACF = lags
                        
        v_x = speed_vectors[:,0]
        v_y = speed_vectors[:,1]
            
        VACFs = np.zeros((2, self.nb_lags))     
        normalized_VACFs = np.zeros((2, self.nb_lags))
            
        for count, lag in enumerate(lags):
            VACFs[0,count] = self.VACF(v_x, int(lag))
            VACFs[1,count] = self.VACF(v_y, int(lag))
     
        normal_v_x = VACFs[0,0]
        normal_v_y = VACFs[1,0]
                
        normalized_VACFs[0,:] = VACFs[0,:]/normal_v_x
        normalized_VACFs[1,:] = VACFs[1,:]/normal_v_y  
        
        return lags_VACF, normalized_VACFs

    
    def process (self):
        
        if self.smoothed:
            speed_vectors = self.data_set['smoothed_speed_vectors']
        else :
            speed_vectors = self.data_set['speed_vectors'] 
            
        lags, VACFs = self.generate_VACFs(speed_vectors)        
       
        self.result_set['statistical_variables']['stochastic'] = {'VACF': {}}
        self.result_set['statistical_variables']['stochastic']['VACF'] = ({'lags': lags,
                                                                            'VACFs': VACFs})
        print("  VACFs generated")
        
        if self.plot:
            self.plot_VACF(lags, 
                           VACFs)
        
        
    def plot_VACF (self, 
                   lags_VACF, 
                   VACFs, 
                   direction = 'both'):
        
        plt.style.use("seaborn")
        fig = plt.figure(figsize=(8,6))
        if direction == 'x':
            plt.plot(lags_VACF, VACFs[0,:], linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
        elif direction == 'y':
            plt.plot(lags_VACF, VACFs[1,:], linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
        else :
            plt.plot(lags_VACF, VACFs[0,:], linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
            plt.plot(lags_VACF, VACFs[1,:], linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
              
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
    
        plt.xlabel("lag", fontsize =9)
        plt.ylabel("VACF", fontsize =9) 
        plt.legend(fontsize = 9)
        
        plt.show()
        plt.clf()
        

    def get_result_set (self):
        return self.result_set
