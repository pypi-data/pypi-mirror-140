# -*- coding: utf-8 -*-

from . import fractal_dimension as ftd
from . import length_over_area as loa
from . import mean_frequency as mf
from . import phase_plane as pp
from . import sway_area_ps as sa
from . import sway_density as swd
from . import velocity as v


def FractalDimension(scan_path,
                     method='H_FD', hilbert_iterations=20, k_max=5, nb_box=5000, fill_factor=500,
                     plot=True):

    data_set = scan_path.get_data_set()
    fractal_analysis = ftd.Fractal_Analysis(data_set,
                                            method, hilbert_iterations, k_max, nb_box, fill_factor,
                                            plot)
    fractal_analysis.process()
    results_set = fractal_analysis.get_result_set()

    fractal_dimension = results_set['statistical_variables']['dynamic']['fractal_dimension']['fractal_dimension']

    return fractal_dimension


def LengthOverArea(scan_path, plot=True):

    data_set = scan_path.get_data_set()
    lfs_analysis = loa.LFS_Analysis(data_set, plot)
    lfs_analysis.process()
    result_set = lfs_analysis.get_result_set()

    lfs = result_set['statistical_variables']['dynamic']['lfs']['lfs']

    return lfs


def MeanFrequency(scan_path, plot=True):

    data_set = scan_path.get_data_set()
    mean_frequency_analysis = mf.Mean_Frequency(data_set, plot)
    mean_frequency_analysis.process()
    result_set = mean_frequency_analysis.get_result_set()

    mean_freq_x = result_set['statistical_variables']['dynamic']['mean_frequency']['mean_freq_x']
    mean_freq_y = result_set['statistical_variables']['dynamic']['mean_frequency']['mean_freq_y']
    mean_freq = result_set['statistical_variables']['dynamic']['mean_frequency']['mean_freq']

    return mean_freq_x, mean_freq_y, mean_freq


def PhasePlane(scan_path, plot=True):

    data_set = scan_path.get_data_set()
    phase_plane_analysis = pp.Phase_Plane_Analysis(data_set, plot)
    phase_plane_analysis.process()
    result_set = phase_plane_analysis.get_result_set()

    std_spd_x = result_set['statistical_variables']['dynamic']['phase_plane']['std_spd_x']
    std_spd_y = result_set['statistical_variables']['dynamic']['phase_plane']['std_spd_y']
    phase_plane_x = result_set['statistical_variables']['dynamic']['phase_plane']['phase_plane_x']
    phase_plane_y = result_set['statistical_variables']['dynamic']['phase_plane']['phase_plane_y']

    return std_spd_x, std_spd_y, phase_plane_x, phase_plane_y


def SwayAreaPS(scan_path, plot=True):

    data_set = scan_path.get_data_set()
    saps_analysis = sa.Sway_Area_ps(data_set, plot)
    saps_analysis.process()
    result_set = saps_analysis.get_result_set()

    saps = result_set['statistical_variables']['dynamic']['sway_area_per_second']['saps']

    return saps


def SwayDensity(scan_path, radius=10, plot=True):

    data_set = scan_path.get_data_set()
    sd_analysis = swd.Sway_Density(data_set, radius, plot)
    sd_analysis.process()
    result_set = sd_analysis.get_result_set()

    sd = result_set['statistical_variables']['dynamic']['sway_density']['SD']
    filtered = result_set['statistical_variables']['dynamic']['sway_density']['filtered']
    i_peaks = result_set['statistical_variables']['dynamic']['sway_density']['i_peaks']
    peaks = result_set['statistical_variables']['dynamic']['sway_density']['peaks']
    mean_peaks = result_set['statistical_variables']['dynamic']['sway_density']['mean_peaks']
    mean_dist_peaks = result_set['statistical_variables']['dynamic']['sway_density']['mean_dist_peaks']

    return sd, filtered, i_peaks, peaks, mean_peaks, mean_dist_peaks


def Velocity(scan_path, plot=True):

    data_set = scan_path.get_data_set()
    v_analysis = v.Velocity_Analysis(data_set, plot)
    v_analysis.process()
    result_set = v_analysis.get_result_set()

    velocity = result_set['statistical_variables']['dynamic']['velocity']['velocity']
    zero_cross = result_set['statistical_variables']['dynamic']['velocity']['zero_cross']
    sl_x = result_set['statistical_variables']['dynamic']['velocity']['sl_x']
    sl_y = result_set['statistical_variables']['dynamic']['velocity']['sl_y']
    sl_tot = result_set['statistical_variables']['dynamic']['velocity']['sl_tot']
    spd_x = result_set['statistical_variables']['dynamic']['velocity']['spd_x']
    spd_y = result_set['statistical_variables']['dynamic']['velocity']['spd_y']
    spd_tot = result_set['statistical_variables']['dynamic']['velocity']['spd_tot']
    peak_x_vel_pos = result_set['statistical_variables']['dynamic']['velocity']['peak_x_vel_pos']
    peak_x_vel_neg = result_set['statistical_variables']['dynamic']['velocity']['peak_x_vel_neg']
    peaks_x_vel = result_set['statistical_variables']['dynamic']['velocity']['peaks_x_vel']
    peak_y_vel_pos = result_set['statistical_variables']['dynamic']['velocity']['peak_y_vel_pos']
    peak_y_vel_neg = result_set['statistical_variables']['dynamic']['velocity']['peak_y_vel_neg']
    peaks_y_vel = result_set['statistical_variables']['dynamic']['velocity']['peaks_y_vel']

    return velocity, zero_cross, sl_x, sl_y, sl_tot, spd_x, spd_y, spd_tot, \
        peak_x_vel_pos, peak_x_vel_neg, peaks_x_vel, \
        peak_y_vel_pos, peak_y_vel_neg, peaks_y_vel
