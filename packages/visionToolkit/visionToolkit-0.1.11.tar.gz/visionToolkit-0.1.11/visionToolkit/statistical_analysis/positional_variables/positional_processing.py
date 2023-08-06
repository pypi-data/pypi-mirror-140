# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import dispersion as dp


def Dispersion(scan_path, smoothed=True, plot=False):

    data_set = scan_path.get_data_set()
    dispersion_analysis = dp.Dispersion(data_set, smoothed=smoothed, plot=plot)

    dispersion_analysis.process()
    result_set = dispersion_analysis.get_result_set()

    statistics = result_set['statistical_variables']['position']

    return statistics 