import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
##import matplotlib as mp
##from scipy.signal import argrelextrema

class ECGData:
    def __init__(self, a_file_name):   
        """Init and load ECG Data from .csv file"""
        self.df_peaks = pd.DataFrame    #dataframe for peak data
        self.df_raw = pd.DataFrame      #dataframe for raw data
        
        if (open(a_file_name, "r") == None):        #check file
            print("FileName not valid!")
            return
        
        column_names = ["Amplitude [mV]", "Time [ms]"]
        self.df_raw = pd.read_csv(a_file_name, sep = ";", header = None, names = column_names)  #read csv to dataframe
        if(self.df_raw.empty):
            print("DataFile was empty!")
            return
        
        print(self.df_raw.head())
        pass


    def detectPeaks(self, a_column=0):
        """Scans the selected column of source-dataframe for Peaks and stores the peak-information in a seperate dataframe"""
        #%% Detect Peaks
        _peak_indices = []                 #indices of the peaks
        _up = -1                      #location of an upwards flank
        _curr = 0                     #current data value in the loop
        _prev = self.df_raw.iloc[0]["Amplitude [mV]"]          #previous data value in the loop

        for row in self.df_raw.iterrows():
            _curr = self.df_raw.iloc[i]["Amplitude [mV]"]          #get 2 adjacent values from data
            _prev = self.df_raw.iloc[i - 1]["Amplitude [mV]"]      

            if _curr > _prev:       #if upwards-flank, remember index
                _up = i

            if (_up > -1) & (_curr < _prev):    #if previously, an upward flank detected, it was a peak
                _peak_indices.append(_up)            #peak start-index is value of _up
                _up = -1

        self.df_peaks = pd.DataFrame(_peak_indices, index=None, columns=["Indizes"])     #create new dataframe from peak indices
        self.df_peaks = self.df_peaks.set_index("Indizes")                          #make peak indices table key
        self.df_peaks["Value"] = self.df_raw.iloc[_peak_indices]["Amplitude [mV]"]          #add peak values
        print(self.df_peaks.head())
        #%% Calculate delta t
        _prev = 0
        _curr = 0
        _next = 0
        _deltaPrev = []
        _deltaNext = []
            
        for i in range(0, len(_peak_indices)):                           #iterate through peaks to get time between each peak
            _curr = self.df_raw.iloc[_peak_indices[i]]["Time [ms]"]
            if i != 0:
                _prev = self.df_raw.iloc[_peak_indices[i - 1]]["Time [ms]"]  
            else:
                _prev = _curr       #if first iteration, _prev = _curr, so that distance to previous = 0

            if i < len(_peak_indices) - 1:
                _next = self.df_raw.iloc[_peak_indices[i + 1]]["Time [ms]"]
            else:
                _next = _curr       #if last iteration, _next = _curr, so that distance to next = 0

            _deltaPrev.append(_curr - _prev)
            _deltaNext.append(_next - _curr)

        self.df_peaks["Next Peak"] = _deltaNext         #add columns to Dataframe
        self.df_peaks["Previous Peak"] = _deltaPrev

        print(self.df_peaks.head())
        pass


    def add_baseline(self):
        """Calculates the vertical distance from each peak to its own baseline"""
        _peak_indices = self.df_peaks.index.values.tolist()     #get all indices of df_peaks
        _rbase_list = []        #the bases right to each peak
        _lbase_list = []        #the bases left to each peak
        _delta_base_list = []   #the distances of each peak to the baseline

        for i in range(0, len(_peak_indices)):
            _step = _peak_indices[i]
            _curr = 0
            _next = 0
            while _step < 2 + len(self.df_raw["Amplitude [mV]"]):      #scan for upwards flank on the right side of the peak
                _curr = self.df_raw.iloc[_step]["Amplitude [mV]"]
                _next = self.df_raw.iloc[_step + 1]["Amplitude [mV]"]  
                if _next > _curr:
                    _rbase_list.append(_step)
                    break
                _step += 1

            _step = _peak_indices[i]
            while _step > 0:            #scan for upwards flank on the left side of the peak
                _curr = self.df_raw.iloc[_step]["Amplitude [mV]"]
                _next = self.df_raw.iloc[_step - 1]["Amplitude [mV]"]  
                if _next > _curr:
                    _lbase_list.append(_step)
                    break
                _step -= 1
            
            _x = _peak_indices[i]       #x pos of the peak 
            _y = self.df_raw.iloc[_peak_indices[i]]["Amplitude [mV]"]  #y pos of the peak
            _xl = _lbase_list[i]        #x pos of the left base                            
            _yl = self.df_raw.iloc[_lbase_list[i]]["Amplitude [mV]"]   #y pos of the left base
            _xr = _rbase_list[i]        #x pos of the right base
            _yr = self.df_raw.iloc[_rbase_list[i]]["Amplitude [mV]"]   #y pos of the right base

            _dbx = _xl - _xr
            _dby = _yl - _yr

            _dpy = _y - _yl
            _dpx = _x - _xl

            _delta_base = _dpy - _dpx * (_dby / _dbx)       #Smart Math
            _delta_base_list.append(_delta_base)

        self.df_peaks["Left Base"] = _lbase_list         #add columns to Dataframe
        self.df_peaks["Right Base"] = _rbase_list
        self.df_peaks["Vert. distance to Baseline"] = _delta_base_list

        print(self.df_peaks.head())
        pass
    

    def plot_time_series(self):
        "Visualizes the data with marked peak locations"
        _peak_indices = self.df_peaks.index.values.tolist()
            
        self.df_raw["Amplitude [mV]"].plot(figsize=(20,8))
        self.df_raw.iloc[_peak_indices]["Amplitude [mV]"].plot(style='.', lw=10, color='red', marker="v")
        #self.df_raw.iloc[_rbase_list + _lbase_list]["Amplitude [mV]"].plot(style='.', lw=10, color='green', marker="^")
        
        if not "Left Base" in self.df_peaks.columns:
            return

        for idx, row in self.df_peaks.iterrows():
            _x = idx
            _y = self.df_raw.iloc[_x]["Amplitude [mV]"]

            _xl = row["Left Base"]
            _yl = self.df_raw.loc[_xl]["Amplitude [mV]"]

            _xr = row["Right Base"]
            _yr = self.df_raw.loc[_xr]["Amplitude [mV]"]

            _delta_base = row["Vert. distance to Baseline"]

            plt.plot([_xl, _xr], [_yl, _yr], color='m', linestyle='--', linewidth=1)
            plt.plot([_x, _x], [_y, _y - _delta_base], color='m', linestyle='--', linewidth=1)

        fig, ax = plt.subplots()

        # Set labels and title
        ax.set_xlabel('Data')
        ax.set_ylabel('Values')
        ax.set_title('Boxplot Example')

        pass
    

## Anlegen einer Zeitreihe der Herzfrequenz aus den EKG-Daten

#%% UC 2.3 Analysieren der Daten auf Abbruch-Kriterium

## Vergleich der Maximalen Herzfrequenz mit Alter des Patienten

#%% UC 2.4 Erstellen einer Zusammenfassung

## Ausgabe einer Zusammenfassung

#%% UC 2.5 Visualisierung der Daten

## Erstellung eines Plots

#%% UC 2.6 Manuelle Eingabe eines Abbruchkritierums

## Abfrage an Nutzer:in, ob Abgebrochen werden soll

#%% UC 2.7 Speichern der Daten

# Speichern der Daten