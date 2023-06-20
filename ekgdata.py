import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import collections

# Klasse EKG-Data für Peakfinder, die uns ermöglicht peaks zu finden
#Änderung


class ECGdata:
    def __init__(self, path):
        '''Methode zum Erstellen eines DataFrames'''
        self.df_peaks = pd.DataFrame
        self.maximal_bpm = 0
        self.minimal_bpm = 0
        self.test_time = 0
        self.average_hr = 0

        column_names = ["Amplitude [mV]", "Time [ms]"]
        self.df_ekg = pd.read_csv(path, sep="\t", header=0, names=column_names)  
        self.find_peaks()


    def find_peaks(self):        
        '''Methode zum Erkennen von Peaks gibt diese als data frame zurück'''
        #------------------Detect Peaks-----------------------
        # Erstellen einer Liste mit den Daten
        np_array = self.df_ekg["Amplitude [mV]"].values
        np_array_time = self.df_ekg["Time [ms]"].values
        # scipy funktion zum Peaks finden
        R_peaks, _ = find_peaks(np_array , height=350)
        #werte aus funktion abspeichern für dataframe
        values = np_array[R_peaks]
        time = np_array_time[R_peaks]
        #dataframe erstellen
        self.df_peaks = pd.DataFrame.from_dict({"Indizes":R_peaks, "Time [ms]":time,"Amplitude [mV]":values})
        
        #------------------Calculate delta t-------------------
        distance_after = []
        for index in self.df_peaks.index:
            if index > len(self.df_peaks.index) - 2:
                break
            #aktuelle nud nächste zeit finden
            aktuelle_zeit = self.df_peaks.iloc[index]["Time [ms]"]
            nachfolgende_zeit = self.df_peaks.iloc[index + 1]["Time [ms]"]
            #Abstände nachher berechnen  
            nachher = nachfolgende_zeit - aktuelle_zeit
            distance_after.append(nachher)

        #Letzten Wert(=0) an Liste anhängen
        distance_after.append(0)
        self.df_peaks ["dt next [ms]"] = distance_after 
        
        #------------------Calculate heartrate---------------------
        momentary_hr = []
        for next in self.df_peaks["dt next [ms]"]:
            if next == 0:
                heartrate = momentary_hr[-1]
            else:
                heartrate = 60000 / next
            momentary_hr.append(heartrate)
                
        self.df_peaks["BPM"] = momentary_hr     


    def get_average_hr(self):
        '''Methode zur ungefähren Berechnung der Herzrate'''
        # Zuerst gibt es keine HR
        self.average_hr = None
        # Nach Blick in die Daten: nur jeder zweite Peak ist eine R-Zacke
        peak_cnt = len(self.df_peaks)
        #Daten sind mit f=1000 Hz aufgezeichnet worden. 1 Beobachtung ist 1 ms
        self.test_time = (self.df_peaks["Time [ms]"][peak_cnt - 1] - self.df_peaks["Time [ms]"][0]) / 1000 / 60
        self.average_hr = peak_cnt / self.test_time
        return self.average_hr

    
    def plot_time_series(self):
        '''Hier ist eine Methode zum Erstellen eines Lineplot'''
        np_array_time = self.df_ekg["Time [ms]"].values
        np_array = self.df_ekg["Amplitude [mV]"].values
        # Ausschnitt festlegen
        ansicht_anfang = 1500
        ansicht_ende = 3500
        x = np_array_time[ansicht_anfang:ansicht_ende]
        y = np_array[ansicht_anfang:ansicht_ende]

        plt.subplot()
        #Scipy-funktion zum Darstellen der peaks
        R_peaks, _ = find_peaks(y, height=350, distance=1)
        T_peaks, _ = find_peaks(y, height=(310,340), distance=1)
        P_peaks, _ = find_peaks(y, height=(302,310), distance=1)
        #Linie erstellen
        plt.plot(x, y)
        #Marker erstellen
        plt.plot(x[R_peaks], y[R_peaks], "x", label="R", color="red")
        plt.plot(x[T_peaks], y[T_peaks], "x", label="T", color="blue" )
        plt.plot(x[P_peaks], y[P_peaks], "x", label="P", color="green")

        plt.xlabel("Time [ms]")
        plt.ylabel("Voltage [mV]")
        plt.title("ECG Data")
        # Wenn das Label "R wave" ist, verdeckt es die erste Welle-> deswegen nur R
        plt.legend(loc='upper left')


    def show_boxplot_distances(self):
        '''Zeige einen Boxplot über die Distanzen zwischen Peaks'''
        boxplot = []
        for distance in self.df_peaks["dt next [ms]"]:
            if distance > 0:
                boxplot.append(distance)

        plt.boxplot(boxplot)
        plt.suptitle("Verteilung der Abstände zwischen den Peaks", fontsize=12, fontweight='bold')
        plt.title ("ohne 0-Abstände", fontsize=12)


    def show_histogram_peaks(self):
        '''Methode zum erstellen eines Histograms der Peaks'''
        plt.hist(self.df_peaks["Amplitude [mV]"])
        plt.title("Histogram of Peaks",  fontsize=12, fontweight='bold')
        plt.xlabel("Value of Peaks in [mV]")
        plt.ylabel("Number of Peaks")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


    def get_hr_info(self):
        '''Methode zum Aufrufen der 3 Methoden für Abstand, Amplitude & Höhe'''
        info = {}
        info["Testdauer"] = self.test_time
        info["Durchschnittlicher_heartrate"] = self.test_time
        info["Minimaler_heartrate"] = self.test_time
        info["Maximaler_heartrate"] = self.test_time

        #print("Testdauer: ", self.test_time)
        #print("Durchschnittlicher heartrate: ", self.average_hr )       
        #print("Minimaler heartrate: ", self.minimal_bpm)
        #print("Maximaler heartrate. ", self.maximal_bpm)

        return info

        
    def show_diagrams(self):
        '''Shows all available plots'''
        print(self.df_peaks.head())
        print(self.df_peaks.tail())

        self.plot_time_series()
        self.show_histogram_peaks()
        self.show_boxplot_distances()
        self.show_histogram_hr()

    
    def show_histogram_hr(self):
        '''Methode zum erstellen eines Histograms der Peaks'''
        plt.subplot()
        plt.hist(self.df_peaks["BPM"][0:len(self.df_peaks)-2])
        plt.title("Histogram of BPM",  fontsize=12, fontweight='bold')
        plt.xlabel("BPM")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
           

    def get_min_hr(self):
        '''Berechnung des Minimalen heartrate'''
        heartrates = self.df_peaks["BPM"]
        heartrates.sort()
        deq = collections.deque(heartrates)
        deq.popleft()
        heartrates = list(deq)
        self.minimal_bpm = heartrates[0]
        print(self.minimal_bpm)
        return self.minimal_bpm


    def get_max_hr(self):
        '''Berechnung des Maximalen heartrate'''
        heartrates = self.df_peaks["BPM"]
        heartrates.sort(reverse=True)
        self.maximal_bpm = heartrates[0]
        print(self.maximal_bpm)    
        return self.maximal_bpm


#my_peakfinder = ECGdata(r"data\ekg_data\01_Ruhe.txt")

#my_peakfinder.heartrate = 10
#my_peakfinder.find_peaks()

#my_peakfinder.get_average_hr()
#my_peakfinder.get_max_hr()
#my_peakfinder.get_min_hr()
#my_peakfinder.get_hr_info()

#my_peakfinder.show_diagrams()