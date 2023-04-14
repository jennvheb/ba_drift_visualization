import math
from shapely.geometry import LineString
import plotly.graph_objs as go
import numpy as np

def get_processinfo(peinfo, clickdata): # peinfo are the actual timestamps and sensor ids and clickdata are the selected x-values from the visualization methods
    realtime = []
    sensorids = []
    ctr = 0
    for i in range(1, len(clickdata)): # for every starting point we have
        if i-1 == 0: #if its the first starting point
            for same in range(len(peinfo[0][1])): # go through first time series
                if math.isclose(round(clickdata[i-1], 2), round(peinfo[0][1][same], 2)) or clickdata[i-1]<peinfo[0][1][same]: # find the clickdata in the time series
                    first = peinfo[0][0][same] # this is the first timestamp in the time series
                    fsensor = peinfo[0][4][0] # these are the sensor ids of the first ats
                    break
        for same in range(len(peinfo[i-1][3])): # go through the average time series
            if math.isclose(round(clickdata[i], 2), round(peinfo[i-1][3][same], 2)) or clickdata[i]<peinfo[i-1][3][same]: # find the clickdata in the average time series
                if ctr == 0:
                    second = peinfo[i-1][2][same] # this is the last timestamp in the average time series
                    realtime.append((first, second))
                    lsensor = peinfo[i-1][4] # these are the sensor ids of the second ats
                    sensorids.append((fsensor,lsensor))
                    ctr = 1
                if ctr == 1:
                    first = peinfo[i-1][5][same] # this is the first timestamp in the last average time series, which becomes the first starting point
                    fsensor = lsensor
                    ctr = 0
                break
    return realtime, sensorids

def prep_segments_to_display(segments_to_displayz, unedited2, tstamps, sensids):
    segments_to_displayx = []
    for elem, segment in enumerate(segments_to_displayz): # iterate through the line segments
            cmp = LineString([(unedited2[elem][0][0], unedited2[elem][0][1]), (unedited2[elem][1][0], unedited2[elem][1][1])]).length
            dduration= abs(unedited2[elem][0][0] - unedited2[elem][1][0]) 
            if elem == 0: # the first line segment is with the time series
                namez = "trace 1 + ats " + str(elem +1)
                segments_to_displayx.append([go.Scatter(x=[segment[0][0]], y=[segment[1][0]],name='x: ' + str(round(segment[0][0], 2)) + ' y: ' + str(round(segment[1][0], 2)),  mode='markers', marker=dict( size=10, color='red'), visible=True)])
            else: namez = "ats " + str(elem) + " + ats "+ str(elem + 1)

            if math.isclose(cmp, 0.05) or cmp > 0.05: # if line segment bigger than set threshold, then it becomes thicker
                if len(segment[0]) == 3: # if there is an offset, that changes the x/y inputs
                    segments_to_displayx.append([go.Scatter(
                        x=(segment[0][0],segment[0][1]) , 
                        y=(segment[1][0], segment[1][1]), 
                        showlegend=False, name='', opacity=0.15,  mode='lines', line=dict(width=3), 
                        hovertemplate='x: %{x}'+'<br>y: %{y} ', visible=True)])
                    segments_to_displayx.append([
                        go.Scatter(x=(segment[0][1],segment[0][2] ), y=(segment[1][1], segment[1][2]),name=namez, 
                                   customdata= np.column_stack(((str(cmp),str(cmp)), (str(tstamps[elem][0]),str(tstamps[elem][0])), (str(tstamps[elem][1]),str(tstamps[elem][1])), (str(sensids[elem][0]),str(sensids[elem][0])), (str(sensids[elem][1]),str(sensids[elem][1])), (str(dduration), str(dduration)))), 
                                   mode='lines+markers', line=dict(width=3), marker=dict(symbol="arrow", size=15, angleref="previous"), 
                                   hovertemplate='x: %{x}'+'<br>y: %{y} ' 
    + '<br>Length in mm: %{customdata[0]}'+ '<br>Duration in sec: %{customdata[5]}'+ '<br> Timestamps from '+ '<br>%{customdata[1]} <br> to <br> %{customdata[2]}' +'<br> First segments sensor IDs: %{customdata[3]}'+ '<br> Second segments sensor IDs: %{customdata[4]}',visible=True)])
                else:
                    segments_to_displayx.append([
                        go.Scatter(x=segment[0], y=segment[1],
                                   customdata= np.column_stack(((str(cmp),str(cmp)), (str(tstamps[elem][0]),str(tstamps[elem][0])), (str(tstamps[elem][1]),str(tstamps[elem][1])), (str(sensids[elem][0]),str(sensids[elem][0])), (str(sensids[elem][1]),str(sensids[elem][1])), (str(dduration), str(dduration)))), 
                                   name=namez,  mode='lines+markers', line=dict(width=3), marker=dict(symbol="arrow", size=15, angleref="previous"),
                                   hovertemplate='x: %{x}'+'<br>y: %{y} ' 
    + '<br>Length in mm: %{customdata[0]}'+ '<br>Duration in sec: %{customdata[5]}'+ '<br> Timestamps from '+ '<br>%{customdata[1]} <br> to <br> %{customdata[2]}' +'<br> First segments sensor IDs: %{customdata[3]}'+ '<br> Second segments sensor IDs: %{customdata[4]}',visible=True)])
            else:
                if len(segment[0]) == 3:
                    segments_to_displayx.append([go.Scatter(
                        x=(segment[0][0],segment[0][1]) , 
                        y=(segment[1][0], segment[1][1]), 
                        showlegend=False, name='', opacity=0.15,  mode='lines', line=dict(width=3), 
                        hovertemplate='x: %{x}'+'<br>y: %{y} ', visible=True)])

                    segments_to_displayx.append([
                        go.Scatter(x=(segment[0][1],segment[0][2] ), y=(segment[1][1], segment[1][2]),name=namez, 
                                   customdata= np.column_stack(((str(cmp),str(cmp)), (str(tstamps[elem][0]),str(tstamps[elem][0])), (str(tstamps[elem][1]),str(tstamps[elem][1])), (str(sensids[elem][0]),str(sensids[elem][0])), (str(sensids[elem][1]),str(sensids[elem][1])), (str(dduration), str(dduration)))), 
                                   mode='lines+markers', line=dict(width=1.5), marker=dict(symbol="arrow", size=10, angleref="previous"),
                                   hovertemplate='x: %{x}'+'<br>y: %{y} '    + '<br>Length in mm: %{customdata[0]}'+ '<br>Duration in sec: %{customdata[5]}'+ '<br> Timestamps from '+ '<br>%{customdata[1]} <br>to<br> %{customdata[2]}' +'<br> First segments sensor IDs: %{customdata[3]}'+ '<br> Second segments sensor IDs: %{customdata[4]}',visible=True)]),
                else:
                    segments_to_displayx.append([
                        go.Scatter(x=segment[0], y=segment[1], 
                                   customdata= np.column_stack(((str(cmp),str(cmp)), (str(tstamps[elem][0]),str(tstamps[elem][0])), (str(tstamps[elem][1]),str(tstamps[elem][1])), (str(sensids[elem][0]),str(sensids[elem][0])), (str(sensids[elem][1]),str(sensids[elem][1])), (str(dduration), str(dduration)))), 
                                   name=namez, mode='lines+markers', line=dict(width=1.5), marker=dict(symbol="arrow", size=10, angleref="previous"), 
                                   hovertemplate='x: %{x}'+'<br>y: %{y} '    + '<br>Length in mm: %{customdata[0]}'+ '<br>Duration in sec: %{customdata[5]}'+ '<br> Timestamps from '+ '<br>%{customdata[1]} <br>to<br> %{customdata[2]}' +'<br> First segments sensor IDs: %{customdata[3]}'+ '<br> Second segments sensor IDs: %{customdata[4]}',visible=True)]),
    segments_to_displayy = [segment for segments_line in segments_to_displayx for segment in segments_line]
    return segments_to_displayy


