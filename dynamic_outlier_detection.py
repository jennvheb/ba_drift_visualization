from sklearn.neighbors import LocalOutlierFactor
from collections import deque
import numpy as np
import math



# set the number of nearest neighbors to use for LOF calculation
n_neighbors = 20

# set the threshold for identifying outliers
n_std = 1.5

contamination = 0.1

# create a LOF model
lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.1)

# initialize an empty list to store outliers
outliers = []

def dynamic_od(sensor_stream, window_size): 
    # i imagine that the sensor reading comes in in preprocess and that i seperate the timestamp from the info there
    # and in preprocess i already seperate it into the different lists and so on
    all_together, sens = sliding_window(sensor_stream, window_size)

#TODO: when we are actually doing it online, then change this method accordingly because as of yet its just a game of guessing what the input is going to look like
def sliding_window(sensor_stream, window_size): 
    window = deque(maxlen=window_size) # create a deque with maximum length of n
    window_info = deque(maxlen=window_size)
    sensor_trace = {}
    sensor_info = {}
    trace_id_old = None
    first_timestamp = None

    while True: # to continously get new sensor data
        timestamp, sensor_value, trace_id_new = sensor_stream.get_values() # we don't know of course
        if trace_id_new == trace_id_old: # if new is the same as old means its still same trace
            sensor_trace = window.pop() # remove unfinished trace
            sensor_info = window_info.pop()
            sensor_trace[timestamp-first_timestamp] = sensor_value
            sensor_info[timestamp] = timestamp-first_timestamp
            sensor_trace.resample()
            sensor_info.resample()
            window.append(sensor_trace)
            window_info.append(sensor_info)
            outlier_detection(window, n_neighbors, contamination, n_std)
            # connection to app has to be made
        else: # it means we have a new trace
            sensor_trace = {}
            sensor_info = {}
            sensor_trace[0] = sensor_value
            sensor_info[timestamp] = 0
            first_timestamp = timestamp
            window.append(sensor_trace)
            window_info.append(sensor_info)
            outlier_detection(window, n_neighbors, contamination, n_std)
            # connect to app has to be made 


def get_window_for_x(window):
    window_for_x = [] # create a list to hold the data points in the window
    indices = []
    for w in range(len(window)): # loop over the traces in the sliding window
        for i, window_x in enumerate(window[w].keys()):
            if math.isclose(round(window_x,2), round(list(window[-1])[-1],2)): # # check if the x value of the data point matches the given x value
                window_for_x.append(window[w][window_x]) # add the data point to the list
                indices.append(i) # from every window every indice
    return window_for_x, indices

def put_back_in_window(window_for_x, window, indices):
    for v in range(len(indices)):
        for w in range(len(window)):
            for i in range(len(window[w].keys())):
                if i == v:
                    window[w][i] = window_for_x[v] # replace the old value with the updated one
                    break
    return window

def outlier_detection(window, n_neighbors, contamination, n_std): 
    window_for_x, indices = get_window_for_x(window)
    if len(window_for_x) < n_neighbors: # if not enough data points, simple replacement with mean
        median = np.median(window_for_x)
        stds = np.std(window_for_x)
        outliers = np.any(np.abs(window_for_x - median) > n_std * stds) # setting n_std depends on the data
        if np.any(outliers):
            window_for_x[outliers] = median
            window = put_back_in_window(window_for_x, window, indices)
            return window
    else:
        clf = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
        y_pred = clf.fit_predict(window_for_x)
        outliers = y_pred == -1 # boolean mask, TRUE is any outliers in y_pred (-1)
        if np.any(outliers):
            centroid = np.mean(window_for_x[~outliers]) 
            window_for_x[outliers] = centroid 
            window = put_back_in_window(window_for_x, window, indices)
        return window
