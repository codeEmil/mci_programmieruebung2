import pandas as pd
import matplotlib.pyplot as plt
import sys
#from scipy.signal import argrelextrema


class EKGdata:

    def __init__(self, path):
        '''Create the DataFrame'''

        columns = ["amplitude [mV]" ,"time [ms]"]
        self.df_ekg = pd.read_csv(path, sep="\t", header=0, names= columns)       
    

    def find_peaks(self):        
        '''Method for Detecting Peaks'''

        #Splitting the columns in seperate lists 
        np_array_amplitude = self.df_ekg["amplitude [mV]"].values
        np_array_time = self.df_ekg["time [ms]"].values

        peaks = []
        peak_times =[]
        
        for index in range(1,len(np_array_amplitude)-1):
            #print("The index is:", index, and the value is np_array_amplitude[index])
            preview = np_array_amplitude[index-1]
            next = np_array_amplitude[index+1]
            current = np_array_amplitude[index]

            if current > next and current > preview: 
            # For each element in the list, define the previous and next element using indexing 
                peaks.append(index)
                peak_times.append(np_array_time[index])

        self.df_peaks = pd.DataFrame({"indices":peaks,"time [ms]":peak_times})
    

    def peaks_information(self):
            '''calling the methods for distance, height and amplitude'''

            self.distance_to_peak()
            self.highest_point_of_peak()
            self.height_of_peak()


    def distance_to_peak(self):
            '''calculating distance between the peaks'''

            #Important: Insert zeros to account for later indexing (filter them out later)
            distance_after =[0]
            distance_before =[0]
            all_distances = [0]
            list_boxplot = []

            for index in self.df_peaks.index:

                if index > 0 and index < len(self.df_peaks)-1:
                    curr_time = self.df_peaks.iloc[index]["time [ms]"]
                    before_time = self.df_peaks.iloc[index-1]["time [ms]"]
                    next_time = self.df_peaks.iloc[index+1]["time [ms]"]
                    
                #Difference to peak before
                    before = curr_time - before_time
                    distance_before.append(before)
                    all_distances.append(before)
                #Differences to peak after  
                    next = next_time - curr_time
                    distance_after.append(next)
                    all_distances.append(next)

            distance_after.append(0)
            distance_before.append(0)
            all_distances.append(0)

            print(distance_after)
            print(distance_before)

            self.df_peaks ["distance to prev peak [ms]"] = distance_before
            self.df_peaks ["distance to next peak [ms]"] = distance_after        
        
        # visualize differences to peak before
            boxplot_before = plt.boxplot(distance_before)
            plt.title("Difference to peak before", fontsize=12, fontweight='bold')
            plt.show()
        # visualize differences to peak after
            boxplot_after = plt.boxplot(distance_after)
            plt.title("Difference to peak after", fontsize=12, fontweight='bold') 
            plt.show()

        #overall distribution
            boxplot_all = plt.boxplot(all_distances)
            plt.title("Overall distribution of the differences between peaks", fontsize=12, fontweight='bold')
            plt.show()
        
        #deleting the zeros from row 49-52
            for distance in distance_after:
                 if distance != 0:
                      list_boxplot.append(distance)

            for distance in distance_before:
                 if distance != 0:
                      list_boxplot.append(distance)

            boxplot_distances = plt.boxplot(list_boxplot)
            plt.suptitle("Distribution of Distances", fontsize=12, fontweight='bold')
            plt.title ("Boxplot without the disorting zeros", fontsize=12)
            plt.show()
            

    def boxplot(self):
        '''creating boxplots for previous and next distances'''
        
        #previous Distances
        plt.boxplot(self.df_peaks["distance to prev peak [ms]"])
        plt.title("distance to the previous peak [ms]", fontsize=12, fontweight='bold')
        plt.show()
        # Next Distances
        plt.boxplot(self.df_peaks["distance to next peak [ms]"])
        plt.title("distance to the next peak [ms]", fontsize=12, fontweight='bold') 
        plt.show()


    def highest_point_of_peak(self):
        '''calculate the highest point of a peak'''

        np_array_amplitude = self.df_ekg["amplitude [mV]"].values
        peak_values = []

        for index in range(1, len(np_array_amplitude) - 1):
            preview = np_array_amplitude[index - 1]
            next = np_array_amplitude[index + 1]
            current = np_array_amplitude[index]

            if current > next and current > preview:
                peak_values.append(np_array_amplitude[index])
        
        self.df_peaks["peak values"] = peak_values

        # visualize the peaks in a histogram
        histogram_peaks = plt.hist(peak_values)
        plt.title("Histogram of the peaks", fontsize=12, fontweight='bold')
        plt.xlabel("Value [mV]")
        plt.ylabel("Number of peaks")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        plt.grid(True)
        plt.show()

    
    def histogram(self):
        '''create method for the histogram'''

        plt.hist(self.df_peaks["peak values"])
        plt.title("Histogram of the peaks",  fontsize=12, fontweight='bold')
        plt.xlabel("Value of peaks [mV]")
        plt.ylabel("Number of peaks")
        plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        plt.grid(True)
        plt.show()

    
    def height_of_peak(self):

        peak_indices = self.df_peaks["indices"].values
        peak_values = self.df_peaks["peak values"].values
        low_indices = self.df_lows.index.values
        low_values = self.df_lows["Low values"].values

        relative_heights = []

        for peak_index, peak_value in zip(peak_indices, peak_values):
            # Find the two nearest low indices around the peak index
            low_indices_before = low_indices[low_indices < peak_index]
            low_indices_after = low_indices[low_indices > peak_index]

            if len(low_indices_before) > 0 and len(low_indices_after) > 0:
                low_index_before = low_indices_before[-1]
                low_index_after = low_indices_after[0]

                # Get the absolute values of the two low points
                low_value_before = low_values[low_index_before]
                low_value_after = low_values[low_index_after]

                # Calculate the average of the two low values
                baseline = (abs(low_value_before) + abs(low_value_after)) / 2

                # Calculate the relative height by subtracting the baseline from the peak value
                relative_height = abs(peak_value) - baseline
                relative_heights.append(relative_height)
            else:
                relative_heights.append(None)

        self.df_peaks["relative height"] = relative_heights

    
    def baseline(self): 

        np_array_amplitude = self.df_ekg["amplitude [mV]"].values
        np_array_time = self.df_ekg["time [ms]"].values

        bases = []
        base_times =[]
        base_values=[]

        for index in range(1,len(np_array_amplitude)-1):
            preview = np_array_amplitude[index-1]
            next = np_array_amplitude[index+1]
            current = np_array_amplitude[index]

            if current < next and current < preview:
                bases.append(index)
                base_times.append(np_array_time[index])
                base_values.append(np_array_amplitude[index])

        print (bases)
        print (base_times)
        print (base_values)
        self.base_times = base_times
        self.df_lows = pd.DataFrame({"Low values":base_values,"time [ms]":base_times})   
    

    def find_bases(self): 

        peak_times = self.df_peaks["time [ms]"]
        peak_values= self.df_peaks["peak values"]

        for peak_time in peak_times:

            if peak_time in peak_times < max(self.base_times):
                index_larger= next(x[0] for x in enumerate(self.base_times) if x[1] > peak_time)
            else:
                index_larger = None

            index_larger
            
            print (peak_values)
            list_copy= self.base_times.copy()
            print(list_copy.reverse()) #reverse the whole list

            if peak_time > max(list_copy):
                index_reverse= next(x[0] for x in enumerate(list_copy) if x[1] < peak_time)
                index_smaller= (len(list_copy)-1) - index_reverse
                print(index_smaller)
            else:
                index_smaller = None
                print(index_smaller)


    def estimate_hr(self):
        '''calculate heartrate'''
       
        self.heat_rate = None
        #every second peak is important
        R_Wave = my_peakfinder.df_peaks.size / 2
        #f = 100Hz
        minutes = my_peakfinder.df_ekg.size / 1000 / 60

        self.heat_rate  = R_Wave / minutes
        
    
    def plot_time_series(self):
        '''creating a lineplot for data'''


        self.fig, self.ax = plt.subplots()
        self.ax.plot(self.df_ekg["time [ms]"], self.df_ekg["amplitude [mV]"])
        self.ax.set_xlabel("time [ms]]")
        self.ax.set_ylabel("voltage [mV]")
        #self.ax.plot(self.df_peaks["time [ms]"],self.df_peaks["peak values"], marker ='x')
        #plt.show()

        self.ax.scatter(self.df_peaks["time [ms]"], self.df_peaks["peak values"], marker="x", color="red")
        plt.grid(True)
        plt.show()

   
my_peakfinder = EKGdata(r"data\01_Ruhe_short.txt")
my_peakfinder.df_ekg
my_peakfinder.find_peaks()
my_peakfinder.distance_to_peak()
my_peakfinder.highest_point_of_peak()
my_peakfinder.df_peaks
my_peakfinder.baseline()
my_peakfinder.find_bases()
#my_peakfinder.boxplot()
my_peakfinder.plot_time_series()

sys.exit(0) #stops the program after the first run
