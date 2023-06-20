import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import collections

# Klasse EKG-Data für Peakfinder, die uns ermöglicht peaks zu finden

class EKGdata:
    def __init__(self, path):
        '''Methode zum Erstellen eines DataFrames'''
        self.df_peaks = pd.DataFrame
        # Definieren der Überschriften
        column_names = ["Amplitude [mV]" ,"Time [ms]"]
        # Pfad für die Daten
        self.df_ekg = pd.read_csv(path, sep="\t", header=0, names= column_names)  


    def find_peaks(self):        
        '''Methode zum Erkennen von Peaks gibt diese als data frame zurück'''
        # Erstellen eine Liste mit den Daten
        np_array = self.df_ekg["Amplitude [mV]"].values
        np_array_time = self.df_ekg["Time [ms]"].values
        # scipy funktion zum Peaks finden
        R_peaks, _ = find_peaks(np_array , height=350)
        #werte aus funktion abspeichern für dataframe
        values = np_array[R_peaks]
        time = np_array_time[R_peaks]
        #dataframe erstellen
        self.df_peaks = pd.DataFrame.from_dict({"Indizes":R_peaks, "Time [ms]":time,"Amplitude [mV]":values})   


    def average_hr(self):
        '''Methode zur ungefähren Berechnung der Herzrate'''
        # Zuerst gibt es keine HR
        self.heart_rate = None
        # Nach Blick in die Daten: nur jeder zweite Peak ist eine R-Zacke
        peak_cnt = len(self.df_peaks)     #TODO - what is my_peakfinder??
        # Daten sind mit f=1000 Hz aufgezeichnet worden. 1 Beobachtung ist 1 ms
        #dauer_signal_in_min = my_peakfinder.df_ekg.size / 1000 / 60
        self.test_time = (self.df_peaks["Time [ms]"][peak_cnt - 1] - self.df_peaks["Time [ms]"][0]) / 1000 / 60
        self.heart_rate  = peak_cnt/self.test_time

    
    def plot_time_series(self):
        '''Hier ist eine Methode zum Erstellen eines Lineplot'''
        np_array_time = my_peakfinder.df_ekg["Time [ms]"].values
        np_array = my_peakfinder.df_ekg["Amplitude [mV]"].values
        #puls= my_peakfinder.df_peaks["BPM"]
        # Ausschnitt festlegen
        slider_index = 1500
        ansicht_anfang = slider_index
        ansicht_ende = slider_index + 2000

        x = np_array_time[ansicht_anfang:ansicht_ende]
        y = np_array[ansicht_anfang:ansicht_ende]
        #z=puls[ansicht_anfang:ansicht_ende]

        plt.plot(x, y)
        #Scipy-funktion zum Darstellen der peaks
        R_peaks, _ = find_peaks(y, height=350, distance =1)
        T_peaks, _ = find_peaks(y, height= (310,340), distance= 1)
        P_peaks, _ = find_peaks(y, height= (302,310), distance =1)
        #Linie erstellen
        #Marker erstellen
        plt.plot(x[R_peaks], y[R_peaks], "x", label="R", color="red")
        plt.plot( x[T_peaks],y[T_peaks], "x", label = "T", color= "blue" )
        plt.plot(x[P_peaks], y[P_peaks], "x", label = "P", color="green")
    
        #z=puls[ansicht_anfang:ansicht_ende]
        #plt.plot(x, z)
        # Wenn das Label "R wave" ist, verdeckt es die erste Welle-> deswegen nur R
        plt.legend(loc='upper left')
        #plt.widgets.Slider(ax=x, valmin = 0, valmax=(len(np_array_time)-2000), *, valinit=0, valfmt=None, closedmin=True, closedmax=True, slidermin=None, slidermax=None, dragging=True)
        plt.show()


    def time_to_next_peak(self):
            '''Abstand zwischen Peaks berechnen'''
            # Listen erstellen
            distance_after = []

            for index in self.df_peaks.index:
                #  Zeitpunkte der peaks finden
                if index < len(self.df_peaks)-1:
                    aktuelle_zeit = self.df_peaks.iloc[index]["Time [ms]"]
                    nachfolgende_zeit = self.df_peaks.iloc[index+1]["Time [ms]"]
                #Abstände nachher berechnen  
                    nachher = nachfolgende_zeit - aktuelle_zeit
                    distance_after.append(nachher)

            #an Listen anhängen
            distance_after.append(0)
            self.df_peaks ["dt next [ms]"] = distance_after  


    def boxplot_distances(self):
        boxplot = []
        for distance in self.df_peaks["dt next [ms]"]:
            if distance > 0:
                boxplot.append(distance)

        plt.boxplot(boxplot)
        plt.suptitle("Verteilung der Abstände zwischen den Peaks", fontsize=12, fontweight='bold')
        plt.title ("ohne 0-Abstände", fontsize=12)
        plt.show()


    def histogram_peaks(self):
        '''Methode zum erstellen eines Histograms der Peaks'''
        plt.hist(self.df_peaks["Amplitude [mV]"])
        plt.title("Histogram of Peaks",  fontsize=12, fontweight='bold')
        plt.xlabel("Value of Peaks in [mV]")
        plt.ylabel("Number of Peaks")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        plt.show()


    def heartrate_info(self):
        '''Methode zum Aufrufen der 3 Methoden
           für Abstand, Amplitude & Höhe'''
        info = {}
        info["Testdauer"] = self.test_time
        info["Durchschnittlicher_Puls"] = self.test_time
        info["Minimaler_Puls"] = self.test_time
        info["Maximaler_Puls"] = self.test_time

        print("Testdauer: ", self.test_time)
        print("Durchschnittlicher Puls: ", self.heart_rate )       
        print("Minimaler Puls: ", self.minimal_bpm)
        print("Maximaler Puls. ", self.maximal_bpm)

        return info

        
    def diagrams(self):
        '''Shows all available plots'''
        print(self.df_peaks.head())
        print(self.df_peaks.tail())

        self.plot_time_series()
        self.histogram_peaks()
        self.boxplot_distances()
        self.histogram_hr()

    
    def momentary_hr(self):
        '''Calculates the momentary heart frequency over time'''
        momentary_hr = []

        for index in self.df_peaks.index:
            if self.df_peaks.iloc[index]["dt next [ms]"] != 0:
                puls = 60000/self.df_peaks.iloc[index]["dt next [ms]"]
                momentary_hr.append(puls)
            else:
                momentary_hr.append(0)

        for next in self.df_peaks["dt next [ms]"]:
            if next == 0:
                puls = momentary_hr[-1]
            else:
                puls = 60000 / next
            momentary_hr.append(puls)
                
        
        #print(momentary_puls)
        self.momentary_hr=momentary_hr
        self.df_peaks ["BPM"] = momentary_hr  
    
    def histogram_hr(self):
        '''Methode zum erstellen eines Histograms der Peaks'''
        plt.hist(self.df_peaks["BPM"][0:len(self.df_peaks)-2])
        plt.title("Histogram of BPM",  fontsize=12, fontweight='bold')
        plt.xlabel("BPM")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        plt.show()  

    def minimal_puls(self):
        '''Berechnung des Minimalen Puls'''
        puls = self.momentary_hr
        self.momentary_hr.sort()
        deq = collections.deque(self.momentary_hr)
        deq.popleft()
        self.momentary_hr = list(deq)
        self.minimal_bpm= self.momentary_hr[0]
        print(self.minimal_bpm)

    def maximal_puls(self):
        '''Berechnung des Maximalen Puls'''
        puls = self.momentary_hr
        puls.sort(reverse=True)
        self.maximal_bpm= puls[0]
        print(self.maximal_bpm)    
    
my_peakfinder = EKGdata(r"data\ekg_data\01_Ruhe.txt")

my_peakfinder.find_peaks()
my_peakfinder.average_hr()
my_peakfinder.time_to_next_peak()
my_peakfinder.momentary_hr()

my_peakfinder.minimal_puls()
my_peakfinder.maximal_puls()

my_peakfinder.heartrate_info()

my_peakfinder.diagrams()