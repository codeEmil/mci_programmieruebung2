import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import collections


class ECGdata:
    def __init__(self, path):
        '''creating a dataframe'''
        self.df_peaks = pd.DataFrame
        column_names = ["Amplitude [mV]", "Time [ms]"]
        self.df_ekg = pd.read_csv(path, sep="\t", header=0, names=column_names)  
        self.find_peaks()


    def find_peaks(self):        
        '''method to find peaks'''
        #------------------detecting the peaks-----------------------
        np_array = self.df_ekg["Amplitude [mV]"].values[::2]
        np_array_time = self.df_ekg["Time [ms]"].values[::2]
        # scipy funktion zum Peaks finden
        R_peaks, _ = find_peaks(np_array , height=350)
        #werte aus funktion abspeichern für dataframe
        values = np_array[R_peaks]
        time = np_array_time[R_peaks]
        #dataframe erstellen
        self.df_peaks = pd.DataFrame.from_dict({"Indizes":R_peaks, "Time [ms]":time,"Amplitude [mV]":values})

        #------------------calculating delta t-------------------
        distance_after = []
        for index in self.df_peaks.index:
            if index > len(self.df_peaks.index) - 2:
                break
            #finding time before and after 
            current_time = self.df_peaks.iloc[index]["Time [ms]"]
            next_time = self.df_peaks.iloc[index + 1]["Time [ms]"]
            #Abstände nachher berechnen  
            difference_next = next_time - current_time
            distance_after.append(difference_next)
        #appending a 0 at the end of the list
        distance_after.append(0)
        self.df_peaks ["dt next [ms]"] = distance_after 
        
        #------------------calculating the heartrate---------------------
        momentary_hr = []
        for next in self.df_peaks["dt next [ms]"]:
            if next == 0:
                heartrate = momentary_hr[-1]
            else:
                heartrate = 60000 / next
            momentary_hr.append(heartrate)
        self.df_peaks["Momentary Beats per Minute"] = momentary_hr 


    def get_average_hr(self):
        '''method to calculate the heartrate '''
        self.average_hr = None
        peak_cnt = len(self.df_peaks)
        #f = 100Hz
        self.test_time = (self.df_peaks["Time [ms]"][peak_cnt - 1] - self.df_peaks["Time [ms]"][0]) / 1000 / 60
        self.average_hr = peak_cnt / self.test_time
        return self.average_hr

    
    def plot_time_series(self):
        '''method to calculate the lineplot with the peaks'''
        np_array_time = self.df_ekg["Time [ms]"].values[::2]
        np_array = self.df_ekg["Amplitude [mV]"].values[::2]
        time = np_array_time
        voltage = np_array
        plt.subplot()
        #Scipy-function finds the peaks
        R_peaks, _ = find_peaks(voltage, height=350, distance=1)
        T_peaks, _ = find_peaks(voltage, height=(310,340), distance=1)
        P_peaks, _ = find_peaks(voltage, height=(302,310), distance=1)
        plt.plot(time, voltage)
        plt.plot(time[R_peaks], voltage[R_peaks], "x", label="R", color="red") #peakmarker
        plt.plot(time[T_peaks], voltage[T_peaks], "x", label="T", color="blue" ) #peakmarker
        plt.plot(time[P_peaks], voltage[P_peaks], "x", label="P", color="green") #peakmarker

        plt.xlabel("Time [ms]")
        plt.ylabel("Voltage [mV]")
        plt.title("ECG Data")
        plt.legend(loc='upper left')


    def show_boxplot_distances(self):
        '''Boxplot with distances between peaks'''
        boxplot = []
        for distance in self.df_peaks["dt next [ms]"]:
            if distance > 0:
                boxplot.append(distance)
        plt.boxplot(boxplot)
        plt.suptitle("Distribution of the distances between the peaks", fontsize=12, fontweight='bold')
        plt.title ("without the zeros", fontsize=12)


    def show_histogram_peaks(self):
        '''Histogram of peaks'''
        plt.hist(self.df_peaks["Amplitude [mV]"])
        plt.title("Histogram of Peaks",  fontsize=12, fontweight='bold')
        plt.xlabel("Value of Peaks in [mV]")
        plt.ylabel("Number of Peaks")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


    def get_hr_info(self):
        '''Method to calculate heart rate information'''
        info = {}
        info["Test Duration"] = self.test_time
        info["Average Heart Rate"] = self.average_hr
        info["Minimum Heart Rate"] = self.minimal_bpm
        info["Maximum Heart Rate"] = self.maximal_bpm
        return info
    
        #print("Testdauer: ", self.test_time, "min / ", self.test_time_sec, "s")
        #print("Durchschnittlicher Puls: ", self.get_average_hr)       
        #print("Minimaler Puls: ", self.get_max_hr)
        #print("Maximaler Puls. ", self.get_min_hr)


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
        plt.hist(self.df_peaks["Momentary Beats per Minute"][0:len(self.df_peaks)-2])
        plt.title("Histogram of BPM",  fontsize=12, fontweight='bold')
        plt.xlabel("Momentary Beats per Minute")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
           

    def get_min_hr(self):
        '''method to calculate the min heartrate'''
        heartrates = self.df_peaks["Momentary Beats per Minute"]
        heartrates.sort()
        deq = collections.deque(heartrates)
        deq.popleft()
        heartrates = list(deq)
        self.minimal_bpm = heartrates[0]
        print(self.minimal_bpm)
        return self.minimal_bpm


    def get_max_hr(self):
        '''method to calculate the max heartrate'''
        heartrates = self.df_peaks["Momentary Beats per Minute"]
        heartrates.sort(reverse=True)
        self.maximal_bpm = heartrates[0]
        print(self.maximal_bpm)    
        return self.maximal_bpm


    def plot_bpm(self):
        '''method to create a line plot of the bpm'''
        #The section could be solved shorter, but the accuracy here is very high!
        verlauf = []
        for index in self.df_peaks.index:
            if index == 0:
                verlauf.append(self.df_peaks.iloc[index]["Momentary Beats per Minute"].mean())
            elif index == 1:
                verlauf.append(self.df_peaks.iloc[index-1:index+1]["Momentary Beats per Minute"].mean())
            elif index == 2:
                verlauf.append(self.df_peaks.iloc[index-2:index+2]["Momentary Beats per Minute"].mean())
            elif index == 3:
                verlauf.append(self.df_peaks.iloc[index-3:index+3]["Momentary Beats per Minute"].mean())
            elif index == 4:
                verlauf.append(self.df_peaks.iloc[index-4:index+4]["Momentary Beats per Minute"].mean())
            elif index == 5:
                verlauf.append(self.df_peaks.iloc[index-5:index+5]["Momentary Beats per Minute"].mean())
            elif index == 6:
                verlauf.append(self.df_peaks.iloc[index-6:index+6]["Momentary Beats per Minute"].mean())
            elif index == 7:
                verlauf.append(self.df_peaks.iloc[index-7:index+7]["Momentary Beats per Minute"].mean())
            elif index == 8:
                verlauf.append(self.df_peaks.iloc[index-8:index+8]["Momentary Beats per Minute"].mean())
            elif index == 9:
                verlauf.append(self.df_peaks.iloc[index-9:index+9]["Momentary Beats per Minute"].mean())
            elif index > 9 and index <= 19:
                verlauf.append(self.df_peaks.iloc[index-10:index+10]["Momentary Beats per Minute"].mean())
            elif index > 19 and index <= 29:
                verlauf.append(self.df_peaks.iloc[index-20:index+20]["Momentary Beats per Minute"].mean())
            elif index > 29 and index <= len(self.df_peaks)-32:
                verlauf.append(self.df_peaks.iloc[index-30:index+30]["Momentary Beats per Minute"].mean())
            elif index  > len(self.df_peaks)-32 and index <= len(self.df_peaks)-22:
                verlauf.append(self.df_peaks.iloc[index-20:index+20]["Momentary Beats per Minute"].mean())
            elif index > len(self.df_peaks)-22  and index <= len(self.df_peaks)-12:
                verlauf.append(self.df_peaks.iloc[index-10:index+10]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-11:
                verlauf.append(self.df_peaks.iloc[index-9:index+9]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-10:
                verlauf.append(self.df_peaks.iloc[index-8:index+8]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-9:
                verlauf.append(self.df_peaks.iloc[index-7:index+7]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-8:
                verlauf.append(self.df_peaks.iloc[index-6:index+6]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-7:
                verlauf.append(self.df_peaks.iloc[index-5:index+5]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-6:
                verlauf.append(self.df_peaks.iloc[index-4:index+4]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-5:
                verlauf.append(self.df_peaks.iloc[index-3:index+3]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-4:
                verlauf.append(self.df_peaks.iloc[index-2:index+2]["Momentary Beats per Minute"].mean())
            elif index == len(self.df_peaks)-3:
                verlauf.append(self.df_peaks.iloc[index-1:index+1]["Momentary Beats per Minute"].mean())
            else:
                verlauf.append(self.df_peaks.iloc[index]["Momentary Beats per Minute"].mean())
        #append data to the dataframe
        self.df_peaks ["Average Heartrate"] = verlauf

        bpm = self.df_peaks["Momentary Beats per Minute"][0:(len(self.df_peaks)-1)][::2]
        time = self.df_peaks["Time [ms]"][0:(len(self.df_peaks)-1)][::2]/1000/60
        average_heartrate = self.df_peaks["Average Heartrate"][0:(len(self.df_peaks)-1)][::2]
        plt.plot(time, bpm, label ="current heartrate")
        plt.title("Heartrate")
        plt.plot(time, average_heartrate ,label ="Average Heartrate", color="orange", linewidth =3)
        plt.axhline(y=80, xmin=0, xmax=len(self.df_peaks)-1, linestyle="--", color="red", linewidth =1, label ="Upper limit of normal values at rest")
        plt.axhline(y=40, xmin=0, xmax=len(self.df_peaks)-1, linestyle="--", color="green", linewidth =1, label ="Lower limit of normal values at rest")
        plt.legend()
        plt.ylabel("Heartrate")
        plt.xlabel("Time [min]")
        plt.show()
