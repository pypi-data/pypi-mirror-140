


import numpy as np
import pandas as pd

from visionToolkit.scan_path_analysis import scan_match as scm
from visionToolkit.scan_path_analysis import multi_match as mlm




def ScanMatch (scan_path_1, scan_path_2,
               smoothed = True, concordance_bonus = None, gap_penalty = 0, 
               h_size = 10, v_size = 10,
               plot = True):

    data_set_1 = scan_path_1.get_data_set()
    data_set_2 = scan_path_2.get_data_set()

    scan_match_analysis = scm.ScanMatch_Analysis(data_set_1, data_set_2,
                                                 smoothed, concordance_bonus, gap_penalty, 
                                                 h_size, v_size, plot)
    scan_match_analysis.process()
    
    result_set = scan_match_analysis.get_result_set()
    
    alignment = result_set['scan_path_variables']['scan_match']['alignement']
    score = result_set['scan_path_variables']['scan_match']['score']
            
    return score, alignment


                    
def MultiMatch (scan_path_1, scan_path_2,
                amplitude_threshold = 1.0, angular_threshold = 20, 
                duration_threshold = 0.1, ratio_duration_length = 0.01,
                smoothed = True, plot = True):
    
    data_set_1 = scan_path_1.get_data_set()
    data_set_2 = scan_path_2.get_data_set()

    multi_match_analysis = mlm.MultiMatch_Analysis(data_set_1, data_set_2,  
                                                   amplitude_threshold, angular_threshold, 
                                                   duration_threshold, ratio_duration_length,
                                                   smoothed, plot)
    multi_match_analysis.process()

    result_set = multi_match_analysis.get_result_set()
    
    shape_score = result_set['scan_path_variables']['multi_match']['shape']
    angular_score = result_set['scan_path_variables']['multi_match']['angular']
    length_score = result_set['scan_path_variables']['multi_match']['length']
    position_score = result_set['scan_path_variables']['multi_match']['position']
    duration_score = result_set['scan_path_variables']['multi_match']['duration']

    return shape_score, angular_score, length_score, position_score, duration_score










































