# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt



class DFA_Analysis():
    
    def __init__(self, 
                 data_set, 
                 daya_type, overlap, nb_lags, q, order,
                 plot):

        self.nb_samples = data_set['nb_samples']-1
        
        self.data_set = data_set        
        self.nb_repetitions = nb_lags
        self.q = q
        self.order = order
        
        self.overlap = overlap
        self.daya_type = daya_type
        self.plot = plot
         
        self.result_set = {'statistical_variables': {}}
          
        self.signal_x = None
        self.signal_y = None
        
        self.fluctuations_x = None
        self.fluctuations_y = None
        self.lags = None


    def find_segments (self, signal, window_length):
        
        if self.overlap == True:
            segments = np.array([signal[i : i + window_length] for i in np.arange(0, self.nb_samples - window_length, window_length // 2)])
            N_t = len(segments)
            
        else:
            segments = signal[: self.nb_samples - (self.nb_samples % window_length)]
            segments = segments.reshape((signal.shape[0] // window_length, window_length))
            N_t = len(segments)
        
        return segments
        
    
    def fractal_dfa_trends(self, segments, window_length):
        
        x = np.arange(window_length)
        coefs = np.polyfit(x[:window_length], segments.T, self.order).T
        #print(coefs)

        trends = np.array([np.polyval(coefs[j], x) for j in np.arange(len(segments))])
        
        return trends
    
    
    def fractal_dfa_fluctuation(self, segments_f, segments_r, trends_f, trends_r):
    
        detrended_f = segments_f - trends_f
        detrended_r = segments_r - trends_r
        
        fluctuation_f = np.sum(detrended_f ** 2, axis=1) / detrended_f.shape[1]
        fluctuation_r = np.sum(detrended_r ** 2, axis=1) / detrended_r.shape[1]
    
        fluctuation = np.power(np.concatenate((fluctuation_f, fluctuation_r)), self.q/2) 
        fluctuation = np.power(np.sum(fluctuation) / len(fluctuation), 1/self.q)
        
        return fluctuation


    def fractal_dfa (self):
        
        fluctuations_x = np.zeros(self.nb_repetitions)
        fluctuations_y = np.zeros(self.nb_repetitions)
        lags = np.zeros(self.nb_repetitions)
        
        for i, w_l in enumerate(10**np.linspace(1,np.log10(self.nb_samples/4), self.nb_repetitions)):
            
            window_length = int(w_l)
            lags[i] = window_length
     
            segments = {}
            trends = {}
    
            segments['x_f'] = self.find_segments(self.signal_x, window_length) 
            segments['x_r'] = self.find_segments(np.flip(self.signal_x), window_length) 
            
            segments['y_f'] = self.find_segments(self.signal_y, window_length) 
            segments['y_r'] = self.find_segments(np.flip(self.signal_y), window_length) 
            
            
            for key in segments.keys():
                trends[key] = self.fractal_dfa_trends(segments[key], window_length)
            
            fluctuations_x[i] = self.fractal_dfa_fluctuation(segments['x_f'], 
                                                             segments['x_r'], 
                                                             trends['x_f'], 
                                                             trends['x_r'])
            fluctuations_y[i] = self.fractal_dfa_fluctuation(segments['y_f'], 
                                                             segments['y_r'], 
                                                             trends['y_f'], 
                                                             trends['y_r'])
        self.fluctuations_x = fluctuations_x
        self.fluctuations_y = fluctuations_y
        self.lags = lags
        
        self.hurst_exponent_x = np.polyfit(np.log10(lags), np.log10(fluctuations_x), 1)[0]
        self.hurst_exponent_y = np.polyfit(np.log10(lags), np.log10(fluctuations_y), 1)[0]

        
    def process (self):
        
        if self.daya_type == "speed":
            #print(self.data_set.keys())
            #X = self.data_set['speed_vectors'][:self.nb_samples]
            X = np.concatenate((self.data_set["x_angle_speed_deg"].reshape(self.nb_samples, 1), 
                                self.data_set["y_angle_speed_deg"].reshape(self.nb_samples, 1)), axis = 1)
            X = X -np.mean(X, axis=0)
            X = np.cumsum(X, axis=0)
            self.signal_x = X[:,0]
            self.signal_y = X[:,1]
            
            
        elif self.daya_type == "position":
            X = np.concatenate((self.data_set["x_angle_deg"].reshape(self.nb_samples+1, 1), 
                                self.data_set["y_angle_deg"].reshape(self.nb_samples+1, 1)), axis = 1)
            X = X[:self.nb_samples]
            X = X -np.mean(X, axis=0)
            X = np.cumsum(X, axis=0)
            self.signal_x = X[:,0]
            self.signal_y = X[:,1] 
        
        self.fractal_dfa()
        
        self.result_set['statistical_variables']['stochastic'] = {'DFA': {}}
        self.result_set['statistical_variables']['stochastic']['DFA'] = ({'lags': self.lags,
                                                                           'fluctuations_x': self.fluctuations_x,
                                                                           'fluctuations_y': self.fluctuations_y})
        to_export = {'DFA polynomial order': self.order,
                     'DFA fractal order': self.q,
                     'horizontal Hurst exponent': self.hurst_exponent_x,
                     'vertical Hurst exponent': self.hurst_exponent_y}
        
        print('\n\n-----------------------------------------------------------------------')
        print("Detrended Fluctuation Analysis")
        print('-----------------------------------------------------------------------\n')

        for feature_name, value in to_export.items():
            if type(value) == str:
                print("\t{0:40}\t {1}".format(feature_name, value))
            else:
                print("\t{0:40}\t {1}".format(feature_name, round(value,3)))
                
        if self.plot:
            self.plot_DFA(self.lags, 
                          self.fluctuations_x, 
                          self.fluctuations_y)
        
        
    def plot_DFA (self, 
                  lags_DFA, 
                  fluctuations_x, 
                  fluctuations_y,
                  direction = 'both'):
        
        plt.style.use("seaborn")
        lg_lags = np.log10(lags_DFA)
        fig = plt.figure(figsize=(8,6))
        
        if direction == 'x':
            plt.plot(lg_lags, np.log10(fluctuations_x), linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
        
        elif direction == 'y':
            plt.plot(lg_lags, np.log10(fluctuations_y), linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
        
        else :
            plt.plot(lg_lags, np.log10(fluctuations_x), linewidth=.4, 
                      label = 'Horizontal axis',
                      color = 'cornflowerblue')
            plt.plot(lg_lags, np.log10(fluctuations_y), linewidth=.4, 
                      label = 'Vertical axis',
                      color = 'indianred')
              
        plt.xticks(fontsize = 7)
        plt.yticks(fontsize = 7)
    
        plt.xlabel("log-lag", fontsize =9)
        plt.ylabel("log-Fluctuations", fontsize =9) 
        plt.legend(fontsize = 9)
        
        plt.show()
        plt.clf()
        
        
    def get_result_set (self):
        return self.result_set      
        
        
        

