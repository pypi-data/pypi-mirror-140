import numpy as np
import pandas as pd


from visionToolkit.physiological_analysis import fixations as fxs
from visionToolkit.physiological_analysis import saccades as scs
from visionToolkit.physiological_analysis import microsaccades as mcs



  

def Fixations (scan_path, method = 'I_VT', fix_threshold = 50, sac_threshold = 50, 
               duration_threshold =50, dispersion_threshold = 7, angular_distance_threshold = 0.35, 
               smoothed = True, plot = True) :
    
    data_set = scan_path.get_data_set()
  
    fixations_analysis = fxs.Fixations_Analysis(data_set, 
                                                method, fix_threshold, sac_threshold, 
                                                duration_threshold, dispersion_threshold, 
                                                angular_distance_threshold, 
                                                smoothed, plot)
    fixations_analysis.process()
    result_set = fixations_analysis.get_result_set()
    
    intervals = result_set['physiological_variables']['fixations']['fixation_intervals']
    centroids = result_set['physiological_variables']['fixations']['centroids']
    
    return intervals, centroids 

 
 
def Saccades (scan_path, method = 'I_VT', fix_threshold = 50, sac_threshold = 100, 
              duration_threshold = 50, dispersion_threshold = 7, angular_distance_threshold = 0.35,
              smoothed = True, plot = True) :
    
    data_set = scan_path.get_data_set()

    saccades_analysis = scs.Saccades_Analysis(data_set, 
                                              method, fix_threshold, sac_threshold, 
                                              duration_threshold, dispersion_threshold, 
                                              angular_distance_threshold, 
                                              smoothed, plot)
    saccades_analysis.process()
    result_set = saccades_analysis.get_result_set()
    
    intervals = result_set['physiological_variables']['saccades']['saccade_intervals']
    
    return intervals



def Microsaccades (scan_path, lambda_threshold = 1.5,
                   smoothed = False, plot = True) :
    
    data_set = scan_path.get_data_set()
    microsaccades_analysis = mcs.Microsaccades_Analysis(data_set, lambda_threshold, 
                                                        smoothed, plot)
    microsaccades_analysis.process()
    result_set = microsaccades_analysis.get_result_set()
    
    intervals = result_set['physiological_variables']['microsaccades']['microsaccade_intervals'] 

    return intervals

















        