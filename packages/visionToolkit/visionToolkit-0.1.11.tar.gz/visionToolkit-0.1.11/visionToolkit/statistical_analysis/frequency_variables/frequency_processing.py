# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from visionToolkit.statistical_analysis.frequency_variables import welch_periodogram as wep



def WelchPeriodogram (scan_path, 
                      nb_per_seg = 256, daya_type = 'position',
                      smoothed = False, plot = True):
    
    data_set = scan_path.get_data_set()
    welch_analysis = wep.Welch_Analysis(data_set, 
                                         nb_per_seg, daya_type,
                                         smoothed, plot)
    welch_analysis.process()
    result_set = welch_analysis.get_result_set() 
    
    frequencies = result_set['statistical_variables']['frequency']['Welch']['frequencies']
    periodogram_x = result_set['statistical_variables']['frequency']['Welch']['periodogramme_horizontal']
    periodogram_y = result_set['statistical_variables']['frequency']['Welch']['periodogramme_vertical']
    
    return frequencies, periodogram_x, periodogram_y

