


import numpy as np
import pandas as pd

from visionToolkit.statistical_analysis.stochastic_variables import MSD as msd
from visionToolkit.statistical_analysis.stochastic_variables import DACF as dacf
from visionToolkit.statistical_analysis.stochastic_variables import VACF as vacf
from visionToolkit.statistical_analysis.stochastic_variables import DFA as dfa



def MSD (scan_path, 
         min_lag = 1, max_lag = 1000, nb_lags = 50,
         smoothed = True, plot = True):
    
    data_set = scan_path.get_data_set()
    msd_analysis = msd.MSD_Analysis(data_set, 
                                    min_lag, max_lag, nb_lags,
                                    smoothed, plot)
    msd_analysis.process()
    result_set = msd_analysis.get_result_set() 
    
    lags = result_set['statistical_variables']['stochastic']['MSD']['lags']
    MSDs = result_set['statistical_variables']['stochastic']['MSD']['MSDs']
    
    return lags, MSDs



def DACF (scan_path, 
          min_lag = 0, max_lag = 500, nb_lags = 100, order = 7,
          smoothed = False, plot = True):
    
    data_set = scan_path.get_data_set()
    dacf_analysis = dacf.DACF_Analysis(data_set, 
                                    min_lag, max_lag, nb_lags, order,
                                    smoothed, plot)
    dacf_analysis.process() 
    result_set = dacf_analysis.get_result_set()   
    
    lags = result_set['statistical_variables']['stochastic']['DACF']['lags']
    DACFs = result_set['statistical_variables']['stochastic']['DACF']['DACFs']

    return lags, DACFs

   
 
def VACF (scan_path,
          min_lag = 0, max_lag = 500, nb_lags = 100,
          smoothed = True, plot = True):
    
    data_set = scan_path.get_data_set()
    vacf_analysis = vacf.VACF_Analysis(data_set, 
                                       min_lag, max_lag, nb_lags,
                                       smoothed, plot)
    vacf_analysis.process() 
    result_set = vacf_analysis.get_result_set()   
    
    lags = result_set['statistical_variables']['stochastic']['VACF']['lags']
    VACFs = result_set['statistical_variables']['stochastic']['VACF']['VACFs']

    return lags, VACFs



def DFA (scan_path, 
         daya_type = 'speed', overlap = True, nb_lags = 25, q = 2, order = 3,
         plot = True):
    
    data_set = scan_path.get_data_set()
    dfa_analysis = dfa.DFA_Analysis(data_set,
                                    daya_type, overlap, nb_lags, q, order,
                                    plot)
    dfa_analysis.process()
    result_set = dfa_analysis.get_result_set()  
   
    lags = result_set['statistical_variables']['stochastic']['DFA']['lags']
    fluctuations_x = result_set['statistical_variables']['stochastic']['DFA']['fluctuations_x']
    fluctuations_y = result_set['statistical_variables']['stochastic']['DFA']['fluctuations_y']

    return lags, fluctuations_x, fluctuations_y



         