import os
from time import time
import yaml
import dateutil.parser as dp
import traces
from datetime import timedelta
import copy
import numpy as np
from scipy import signal
import math


# import the files and transform into time series

def read(directory):
    filenames = []

    #get and go through index.txt
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            f = os.path.join(directory, filename)
            with open(f, 'r') as lines:
                next(lines) #skip first line of doc
                for events in lines:
                    for words in events.split():
                        if "(" in words:
                            filenames.append(words[1:-1]) # so here are the filenames without the yaml extension

    time_sequence, all_peinfo = make_traces(filenames, directory)

    return time_sequence, all_peinfo

def make_traces(filenames, directory):
    overlog = dict()
    logs = dict() 
    all_peinfo = dict()
    single_peinfo = dict()

    for filename in filenames:
            f = os.path.join(directory, filename + ".xes.yaml")
            with open(f, 'r') as stream: # open a file
                for data in yaml.safe_load_all(stream): # all seperated data within the file (e.g. log, event, event, event, ...)
                        time_sequence = traces.TimeSeries()
                        timestampss = traces.TimeSeries()
                        time_series = {}
                        if 'log' in data:
                            if 'Machining V2' != data['log']['trace']['cpee:name']: # just one sensor for now
                                break
                            else:
                                sensor_id = data['log']['trace']['concept:name']
                        if 'event' in data:
                                    for k, v in data['event'].items(): 
                                        if v == "activity/receiving": 
                                            for k, v in data['event']['data']['data_receiver'][0].items():
                                                if k == 'data':  
                                                    ctr = 0
                                                    for i in range(len(v)): # one doc in the file
                                                        if v[i]['ID'] == 'keyence/measurement':
                                                            if v[i]['value'] != 999.99: # filter out 999.99
                                                                if ctr == 0:
                                                                    time_sequence[0] = v[i]['value']
                                                                    time_series[0] = v[i]['value']
                                                                    timestampss[dp.parse(v[i]['timestamp'])] = 0
                                                                    ctr= 1
                                                                if ctr != 0:
                                                                    parsed_t = dp.parse(v[0]['timestamp'])
                                                                    parsed_2 = dp.parse(v[i]['timestamp'])
                                                                    
                                                                    t_in_seconds = parsed_t.timestamp() # here are the seconds
                                                                    two_in_seconds = parsed_2.timestamp() 
                                                                    time_sequence[two_in_seconds-t_in_seconds] = v[i]['value']
                                                                    time_series[two_in_seconds-t_in_seconds] = v[i]['value']

                                                                    timestampss[dp.parse(v[i]['timestamp'])] = two_in_seconds-t_in_seconds
   
                                                    
                                                    if len(time_sequence) > 0:

                                                        regular = time_sequence.sample( #resample the time sequence to equidistant time series
                                                            sampling_period=0.05,
                                                            start= time_sequence.first_key(),
                                                            end= time_sequence.last_key(),
                                                            interpolate='linear'
                                                        )
                                                                                                               
                                                        tmp = dict()
                                                        for tme, elem in regular:
                                                            tmp[tme] = elem
                                                        
                                                        logs[sensor_id] = tmp
                                                   
                                                                                                    
                                                    if len(timestampss) > 0:

                                                        regular = timestampss.sample( # resample the process info in same period as the time series
                                                            sampling_period=0.05,
                                                            start= timestampss.first_key(),
                                                            end= timestampss.last_key(),
                                                            interpolate='linear'
                                                        )
                                                                                                                
                                                        tmp = dict()
                                                        for tme, elem in regular:
                                                            tmp[tme] = elem
                                                        single_peinfo[sensor_id] = tmp
                                                    

    if len(logs) > 0:
        overlog['Machining V2'] = logs # time series
        all_peinfo['Machining V2'] = single_peinfo # process execution information

    
    return overlog, all_peinfo
