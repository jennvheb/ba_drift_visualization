import enum
from re import I
import copy
from tkinter import W
import numpy as np
from tslearn.barycenters import dtw_barycenter_averaging
from tslearn.utils import to_time_series_dataset
from collections import deque

def static_od(time_sequence, all_peinfo, window_size, max_group_size):
    all_together, sens = sliding_window(time_sequence, all_peinfo, window_size, max_group_size)
    return all_together, sens

def sliding_window(time_sequence, all_peinfo, window_size, max_group_size):
    window = deque(maxlen=window_size) # create a deque with maximum length of n
    window_info = deque(maxlen=window_size)
    
    for w in time_sequence.keys(): # loop over the data stream
        for e, t in enumerate(time_sequence[w].keys()):
                window.append(time_sequence[w][t]) # add the new data points to the window
                if e == len(time_sequence[w])-1: # check if its the last time series 
                    for a, again in enumerate(all_peinfo[w].items()):  # loop over the process execution information
                        window_info.append(again) 
                        if a == len(all_peinfo[w])-1: # if at last time series and last proc exec info
                            all_together, sens = outlier_detection(window, window_info, max_group_size)
    return all_together, sens
     
def outlier_detection(time_sequence, all_peinfo, max_groupsize): 
    # time sequence is overlog['Machining V2'] = logs, logs[sensor_id] = tmp, tmp[tme] = elem
    # the following code is adapted from F. Stertz, S. Rinderle-Ma, and J. Mangler, “Analyzing process concept drifts based on sensor event streams during runtime", 2020

    ats_x = dict() 
    ats_y = dict()
    all_together = []
    sens = []
    uhatsx = dict()
    ahatsy = dict()
    sstats = []
    tmp_ts_list = []
    process_exec_info = []

    for t in range(len(time_sequence)): 
        if len(time_sequence[t]) > 2:               
            tmp_ts_list.append(time_sequence[t]) 
            process_exec_info.append(all_peinfo[t]) 
            sstats.append(len(time_sequence[t])) 
        
    q3, q1 = np.percentile(sstats, [75, 25])
    iqr = q3-q1 
    no_sh = q1 - 1.5 * iqr
    no_ln = q3 + 1.5 * iqr
    ts_list = []
    againagain = []
    
    for index, t in enumerate(tmp_ts_list):
        if len(t) > no_sh and len(t) < no_ln:
            ts_list.append(t)
            againagain.append(process_exec_info[index])
    
    max_elements = max_groupsize
    time_s_for_dtw = []
    infoingroups = []
    
    for i, e in enumerate(ts_list):

        if len(time_s_for_dtw) < max_elements:
            time_s_for_dtw.append(e)
            infoingroups.append(againagain[i])
        if len(time_s_for_dtw) == max_elements or i == len(ts_list)-1: # if the length of the new array is 2 or the rounded number OR the index is at the last element in the group (meaning it doesnt have to be a full group)

            time_s_x = []
            time_s_y= []
            proc_exec_x = []
            proc_exec_y = []
            proc_exec_sensorids = []
   
            for i in range(len(time_s_for_dtw)):
                time_s_x.append(list(time_s_for_dtw[i].keys()))
                time_s_y.append(list(time_s_for_dtw[i].values()))

            to_ts = to_time_series_dataset(time_s_y) 
            ats_y = dtw_barycenter_averaging(to_ts)  
            list_max = filter(lambda i: len(i) == max([len(l) for l in time_s_x]), time_s_x) # dtw returns from a list of time series, an ats with the length of the longest time series, so we need to find to match that here
            ats_x = list(list_max)

            for i in range(len(infoingroups)):
                proc_exec_sensorids.append(infoingroups[i][0])
                proc_exec_x.append(list(infoingroups[i][1].keys()))
                proc_exec_y.append(list(infoingroups[i][1].values()))
            
            proc_ex_ats = dtw_barycenter_averaging(proc_exec_y)
           
            list_max = filter(lambda i: len(i) == max([len(l) for l in proc_exec_x]), proc_exec_x)
            last_ats = proc_exec_x[-1]   
            first_ats = proc_exec_x[0]

            all_together.append((ats_x, ats_y, time_s_x, time_s_y))
            sens.append((proc_exec_x[0], proc_exec_y[0], last_ats, proc_ex_ats.ravel(), proc_exec_sensorids, first_ats)) 
         
            time_s_for_dtw.clear()
            infoingroups.clear()

    return all_together, sens

