# -*- coding: utf-8 -*-

from scipy.signal import savgol_filter
import pandas as pd
import numpy as np


class Velocity_Analysis():

    def __init__(self,
                 data_set,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set

        self.delta_t = 1/data_set['sampling_frequency']

        self.result_set = {'statistical_variables': {}}
        self.plot = plot

        self.velocity = None
        self.zero_cross = None
        self.sl_x, self.sl_y, self.sl_tot = None, None, None
        self.spd_x, self.spd_y, self.spd_tot = None, None, None
        self.peak_x_vel_pos, self.peak_x_vel_neg, self.peaks_x_vel = None, None, None
        self.peak_y_vel_pos, self.peak_y_vel_neg, self.peaks_y_vel = None, None, None

    def compute_velocity(self):
        """

            ***** REQUIRES A COLUMN WITH THE TIME IN THE data_set *****
                    (Or we can use self.delta_t if we consider that
                    the recording is perfect with no variations in Fs)

        We use a low-pass filter to remove the high  frequency components of the noise.
        We use a Savitsky–Golay filter with a polynomial of order 3 and a filter window of length 5
        because we do not know the threshold that separates the noise from real-world measurements.
        """

        # Savitzky–Golay filters with a window size of length 5 and a polynomial of order 3
        # NaN values have to be removed. Here they are simply replaced by zeros
        x_filt = savgol_filter(np.nan_to_num(self.data_set['x_array']),
                               window_length=5,
                               polyorder=3)
        y_filt = savgol_filter(np.nan_to_num(self.data_set['y_array']),
                               window_length=5,
                               polyorder=3)

        # Compute velocity
        velocity = pd.DataFrame(data={'dt': self.data_set['Recording timestamp [μs]'],
                                      'v_x (px/s)': x_filt,
                                      'v_y (px/s)': y_filt})
        velocity = velocity.diff()
        velocity = velocity[['v_x (px/s)',
                             'v_y (px/s)']].div(velocity.dt*(10**-6), axis=0)

        return velocity

    def zero_crossing(velocity):

        # Finds the zero crossings (of velocity)
        # Returns the position right after the zero crossing

        # Zero crossing x
        zeros_x = np.where(np.diff(np.signbit(velocity['v_x (px/s)'])))[0] + 1

        # Zero crossing y
        zeros_y = np.where(np.diff(np.signbit(velocity['v_y (px/s)'])))[0] + 1

        return np.sum(zeros_x), np.sum(zeros_y)

    def compute_mean_velocity(self):

        # Convert numpy array into pandas DataFrame
        df_dataset = pd.DataFrame(data={
            'x_array': self.data_set['x_array'],
            'y_array': self.data_set['y_array']
        })
        diff = df_dataset.diff().abs()

        # Sway length
        # Sway length x
        sl_x = np.sum(diff['x_array'])
        # Sway length y
        sl_y = np.sum(diff['y_array'])
        # Sway length total
        sl_tot = np.sum(np.sqrt(diff['x_array']**2 +
                                diff['x_array']**2))

        # Sway path
        T = self.nb_samples
        # Mean SPD x
        spd_x = sl_x/T
        # Mean SPD y
        spd_y = sl_y/T
        # Mean SPD total
        spd_tot = sl_tot/T

        return sl_x, sl_y, sl_tot, spd_x, spd_y, spd_tot

    def velocity_peak(velocity):

        # Reset index
        velocity.reset_index(drop=True, inplace=True)

        zeros_x = np.where(np.diff(np.signbit(velocity['v_x (px/s)'])))[0] + 1
        zeros_y = np.where(np.diff(np.signbit(velocity['v_y (px/s)'])))[0] + 1

        # x
        peaks_x = []
        for i1, i2 in zip(zeros_x[:-1], zeros_x[1:]):
            # Cut velocity dataframe
            cut = velocity['v_x (px/s)'][i1+1:i2]
            # Get peak
            if len(cut) == 0:
                continue
            peaks_x.append(max(cut, key=abs))

        # Positive peaks
        peaks_pos = np.array(peaks_x)[np.where(np.array(peaks_x) > 0)]
        peak_x_vel_pos = np.mean(peaks_pos)

        # Negative peaks
        peaks_neg = np.array(peaks_x)[np.where(np.array(peaks_x) < 0)]
        peak_x_vel_neg = np.mean(peaks_neg)

        # All peaks
        peaks_x_vel = np.mean(peaks_x)

        # y
        peaks_y = []
        for i1, i2 in zip(zeros_y[:-1], zeros_y[1:]):
            # Cut velocity dataframe
            cut = velocity['v_y (px/s)'][i1+1:i2]
            # Get peak
            if len(cut) == 0:
                continue
            peaks_y.append(max(cut, key=abs))

        # Positive peaks
        peaks_pos = np.array(peaks_y)[np.where(np.array(peaks_y) > 0)]
        peak_y_vel_pos = np.mean(peaks_pos)

        # Negative peaks
        peaks_neg = np.array(peaks_y)[np.where(np.array(peaks_y) < 0)]
        peak_y_vel_neg = np.mean(peaks_neg)

        # All peaks
        peaks_y_vel = np.mean(peaks_y)

        return peak_x_vel_pos, peak_x_vel_neg, peaks_x_vel, peak_y_vel_pos, peak_y_vel_neg, peaks_y_vel

    def process(self):

        self.velocity = self.compute_velocity()
        self.zero_cross = self.zero_crossing(self.velocity)
        self.sl_x, self.sl_y, self.sl_tot, \
            self.spd_x, self.spd_y, self.spd_tot = self.compute_mean_velocity()
        self.peak_x_vel_pos, self.peak_x_vel_neg, self.peaks_x_vel, \
            self.peak_y_vel_pos, self.peak_y_vel_neg, self.peaks_y_vel = self.velocity_peak(
                self.velocity)

        self.result_set['statistical_variables']['dynamic'] = {
            'velocity': {}}
        self.result_set['statistical_variables']['dynamic']['velocity'] = (
            {'velocity': self.velocity,
             'zero_cross': self.zero_cross,
             'sl_x': self.sl_x,
             'sl_y': self.sl_y,
             'sl_tot': self.sl_tot,
             'spd_x': self.spd_x,
             'spd_y': self.spd_y,
             'spd_tot': self.spd_tot,
             'peak_x_vel_pos': self.peak_x_vel_pos,
             'peak_x_vel_neg': self.peak_x_vel_neg,
             'peaks_x_vel': self.peaks_x_vel,
             'peak_y_vel_pos': self.peak_y_vel_pos,
             'peak_y_vel_neg': self.peak_y_vel_neg,
             'peaks_y_vel': self.peaks_y_vel})

    def get_result_set(self):
        return self.result_set
