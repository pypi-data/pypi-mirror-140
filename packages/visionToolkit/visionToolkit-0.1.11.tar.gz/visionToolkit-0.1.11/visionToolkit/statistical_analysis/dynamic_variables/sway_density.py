import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


class Sway_Density():

    def __init__(self,
                 data_set,
                 radius,
                 plot):

        self.nb_samples = data_set['nb_samples']
        self.data_set = data_set

        self.delta_t = 1/data_set['sampling_frequency']
        self.radius = radius

        self.result_set = {'statistical_variables': {}}
        self.plot = plot

        self.SD = None
        self.filtered = None
        self.i_peaks = None
        self.peaks = None
        self.mean_peaks = None
        self.mean_dist_peaks = None

    def compute_sway_density(self):

        Fs = 1/self.delta_t

        SD = []
        for i_n, (x_n, y_n) in enumerate(zip(self.data_set['x_array'],
                                             self.data_set['y_array'])):
            SD_pos = 0
            SD_neg = 0

            # SD+
            for x_p, y_p in zip(self.data_set['x_array'][i_n+1:],
                                self.data_set['y_array'][i_n+1:]):
                if np.sqrt((x_p-x_n)**2 + (y_p-y_n)**2) <= self.radius:
                    SD_pos += 1
                else:
                    break
            # SD-
            if i_n >= 1:
                for x_p, y_p in zip(self.data_set['x_array'][i_n-1::-1],
                                    self.data_set['y_array'][i_n-1::-1]):
                    if np.sqrt((x_p-x_n)**2 + (y_p-y_n)**2) <= self.radius:
                        SD_neg += 1
                    else:
                        break

            SD.append((SD_pos+SD_neg)/Fs)

        return SD

    def filtering(self, SD, fc=2.5):
        """
        fc = Cut-off frequency of the filter
        """
        Fs = 1/self.delta_t
        w = fc / (Fs/2)  # Normalize the frequency
        b, a = butter(4, w, 'low')  # Butterworth filter of order 4

        return filtfilt(b, a, SD)

    def peaks_sway_density(self, SD, distance):
        """
        Finds the peaks of sway density.
        The sway density signal is first low-pass filtered with a Butterworth filter of
        order 4 (Jacono et al., 2004). The peaks are found using scipy's find_peaks.
        distance is the minimal horizontal distance (>= 1) in samples between neighbouring peaks.
        """

        # Mean sway density peak
        if distance == None:
            # distance defaults to 1s between peaks
            distance = 1/self.delta_t
        # i_peaks, _ = find_peaks(SD, distance=distance)
        i_peaks, _ = find_peaks(SD)
        peaks = np.array(SD)[i_peaks]
        mean_peaks = np.mean(peaks)

        # Mean spatial distance between sway density peaks
        # Conversion in pandas DataFrame because it's easier
        df_dataset = pd.DataFrame(data={
            'x_array': self.data_set['x_array'],
            'y_array': self.data_set['y_array'],
        })
        peaks_data = df_dataset.iloc[i_peaks]
        diff = peaks_data[['x_array',
                           'y_array']].diff()
        mean_dist_peaks = np.sum(
            np.sqrt(diff['x_array']**2 + diff['y_array']**2))

        return i_peaks, peaks, mean_peaks, mean_dist_peaks

    def plot_sway_density(self, SD, i_peaks, filtered):

        _, ax = plt.subplots(figsize=(12, 6))
        ax.plot(SD)
        ax.set_xlabel('Time', fontsize=15)
        ax.set_ylabel('Sway density', fontsize=15)
        plt.show()

        _, ax = plt.subplots(figsize=(12, 6))
        ax.plot(filtered)
        for i in i_peaks:
            ax.axvline(i, c='k', linestyle='--', alpha=0.3)
        ax.set_xlabel('Time', fontsize=15)
        ax.set_ylabel('Filtered sway density', fontsize=15)

        plt.show()

        return

    def process(self):

        self.SD = self.compute_sway_density()
        self.filtered = self.filtering(self.SD, fc=2.5)
        self.i_peaks, self.peaks, self.mean_peaks, self.mean_dist_peaks = self.peaks_sway_density(
            self.filtered, distance=1/self.delta_t)

        if self.plot:
            self.plot_sway_density(self.SD, self.i_peaks, self.filtered)

        self.result_set['statistical_variables']['dynamic'] = {
            'sway_density': {}}
        self.result_set['statistical_variables']['dynamic']['sway_density'] = (
            {'SD': self.SD,
             'filtered': self.filtered,
             'i_peaks': self.i_peaks,
             'peaks': self.peaks,
             'mean_peaks': self.mean_peaks,
             'mean_dist_peaks': self.mean_dist_peaks})

    def get_result_set(self):
        return self.result_set
