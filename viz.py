import numpy as np
from shapely.geometry import LineString, Point, MultiLineString
import math
import sys
import numpy as np


def calculate_shortest_distance(ats, point_x, scale_factor, offset): #code description in thesis
    line_segments = []
    proc_exec = []
    p1 = get_point(ats, point_x)
    line_ts = LineString(np.column_stack((ats[0][0][0], ats[0][1].ravel())))
    closest_point = line_ts.interpolate(line_ts.project(p1))
    proc_exec.append(p1.x)
    line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
    for n in range(len(ats)-1):
        proc_exec.append(closest_point.x)
        p1 = closest_point
        line_ts = LineString(np.column_stack((ats[n+1][0][0], ats[n+1][1].ravel())))
        closest_point = line_ts.interpolate(line_ts.project(p1))
        line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
        if n == len(ats)-2:
            proc_exec.append(closest_point.x)
    scaled_lengths = scale_lengths(line_segments, scale_factor)
    scaled_and_spaced_lengths = add_offset(scaled_lengths,  offset)
    return scaled_and_spaced_lengths, line_segments, proc_exec
            
def scale_lengths(line_segments, scale_factor):
    diff = []
    scaled_lengths = []
    for z in range(len(line_segments)):
        diff.append(LineString(line_segments[z]).length) # get the original lengths of the line segments
    for d , k in enumerate(diff):
        slps = cst_slope(line_segments[d][0][0], line_segments[d][0][1], line_segments[d][1][0], line_segments[d][1][1]) # getting the slope of the line segment
        if d == 0:
            start = Point(line_segments[0][0][0], line_segments[0][0][1]) # this is what the length should be, slps[d] is the slope it stays the same
        else:
            start = end
        dx = k*scale_factor / math.sqrt(1 + math.pow(slps, 2)) # scaling the line and reconstructing it
        dy = slps * dx
        if((line_segments[d][0][0] < line_segments[d][1][0]) or ((line_segments[d][0][0]-line_segments[d][1][0]) == 0 and line_segments[d][0][1] < line_segments[d][1][1])): # if the direction of the original segment is up/right 
            line = LineString([start, (start.x + dx, start.y + dy)])
        else: # if the direction of the original segment is down/left
            line = LineString([start, (start.x - dx, start.y - dy)])
        end = Point(line.coords[-1]) # get the endpoint of the line       
        scaled_lengths.append(((start.x, start.y), (end.x, end.y)))
    return scaled_lengths

def add_offset(line_segments, offset):
    acc_offset_x = 0
    acc_offset_y = 0
    scaled_and_spaced = []
    nx1 = line_segments[0][0][0] # initialize the first endpoints
    nx3 = line_segments[0][1][0]
    ny1 = line_segments[0][0][1]
    ny3 = line_segments[0][1][1] 
    scaled_and_spaced.append([(nx1, nx3), (ny1, ny3)])
    for i in range(1, len(line_segments)): # go through every line segment
        p2_start = line_segments[i][0]
        p2_end = line_segments[i][1]
        p1_start = line_segments[i-1][0]
        p1_end = line_segments[i-1][1]
        if abs(p2_start[0] - p2_end[0]) < abs(p2_start[1] - p2_end[1]): # the diff for x is smaller that means we are closer to vertical than horizontal -> offset to x
            if  (p1_start[1] < p1_end[1] and p2_start[1] > p2_end[1]) or (p1_start[1] > p1_end[1] and p2_start[1] < p2_end[1]): # if the directions of the two line segments are different
                acc_offset_x += offset
                nx1 = nx3
                nx2 = nx3 + offset  
                nx3 = line_segments[i][1][0] + acc_offset_x
                ny1 = ny3
                ny2 = ny3 
                ny3 = line_segments[i][1][1]  
                scaled_and_spaced.append([(nx1, nx2,  nx3), (ny1, ny2, ny3)])
            else: # nothing happens, the line segments go in the same direction, just accumulated offset is transfered
                nx1 = nx3
                nx2 = nx3
                nx3 = line_segments[i][1][0] + acc_offset_x
                ny1 = ny3
                nx2 = nx3
                ny3 = line_segments[i][1][1]  + acc_offset_y
                scaled_and_spaced.append([(nx1, nx3), (ny1, ny3)])
        else: # offset to y
            if  (p1_start[0] < p1_end[0] and p2_start[0] > p2_end[0]) or (p1_start[0] > p1_end[0] and p2_start[0] < p2_end[0]): 
                acc_offset_y -= offset
                nx1 = nx3
                nx2 = nx3   #ctr is fixed, newctr at the start 0
                nx3 = line_segments[i][1][0] 
                ny1 = ny3
                ny2 = ny3 - offset
                ny3 = line_segments[i][1][1]  + acc_offset_y
                scaled_and_spaced.append([(nx1, nx2, nx3),  (ny1, ny2, ny3)])
            else:
                nx1 = nx3
                nx2 = nx3
                nx3 = line_segments[i][1][0] + acc_offset_x
                ny1 = ny3
                nx2 = nx3
                ny3 = line_segments[i][1][1]  + acc_offset_y
                scaled_and_spaced.append([(nx1, nx3), (ny1, ny3)])
    return scaled_and_spaced

def get_point(ats, point_x): #code description in thesis
    for u in range(len(ats[0][2][0])-1): # this is the x values of the first time series
        if ats[0][2][0][u] >= point_x:
            p1 = Point(ats[0][2][0][u], ats[0][3][0][u])
            return p1 

def get_perp_line(original, p1, dist, line_ts): #code description in thesis
    # find two points on the time series, equidistant from p1
    point1 = original.interpolate(original.project(p1) - dist) 
    point2 = original.interpolate(original.project(p1) + dist) 
    slope = (point2.y - point1.y) / (point2.x - point1.x)
    # find the slope of a line perpendicular to the line passing through point1 and point2
    perpendicular_slope = -1 / slope
    # find the y-intercept of the line perpendicular to the line passing through point1 and point2 and passing through nearest_point
    y_intercept = p1.y - perpendicular_slope * p1.x
    # create a LineString that passes through nearest_point and is perpendicular to the line passing through point1 and point2
    cd = LineString([(p1.x - 100000, perpendicular_slope * (p1.x - 100000) + y_intercept), (p1.x + 100000, perpendicular_slope * (p1.x + 100000) + y_intercept)])
    intersections = cd.intersection(line_ts)
    return intersections

def identify_intersection(intersections, known_point, line_ts): #code description in thesis
    if intersections.geom_type == 'MultiPoint':
        distances_to_known = [known_point.distance(point) for point in list(intersections.geoms)]
        closest_index = distances_to_known.index(min(distances_to_known))
        closest_point = list(intersections.geoms)[closest_index]
    elif intersections.geom_type == 'Point':
        closest_point = intersections
    else:
        closest_point = line_ts.interpolate(line_ts.project(known_point))
    return closest_point
        
def calculate_segments_angles(ats, point_x, scale_factor, offset, distance): #code description in thesis
    line_segments = []
    proc_exec = []
    dist = distance
    p1 = get_point(ats, point_x)
    original = LineString(np.column_stack((ats[0][2][0], ats[0][3][0])))
    line_ts = LineString(np.column_stack((ats[0][0][0], ats[0][1].ravel())))
    intersections = get_perp_line(original, p1, dist, line_ts)
    closest_point = identify_intersection(intersections, p1, line_ts)
    proc_exec.append(p1.x)
    line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
    for n in range(len(ats)-1): 
        proc_exec.append(closest_point.x)
        p1 = closest_point
        original = LineString(np.column_stack((ats[n][0][0], ats[n][1].ravel())))
        line_ts = LineString(np.column_stack((ats[n+1][0][0], ats[n+1][1].ravel())))
        intersections = get_perp_line(original, p1, dist, line_ts)
        closest_point = identify_intersection(intersections, p1, line_ts)
        line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
        if n == len(ats)-2:
            proc_exec.append(closest_point.x)
    scaled_lengths = scale_lengths(line_segments, scale_factor)
    scaled_and_spaced_lengths = add_offset(scaled_lengths, offset)
    return scaled_and_spaced_lengths, line_segments, proc_exec

def calculate_segments_straight_up(ats, point_x, scale_factor, offset): #code description in thesis
    line_segments = []
    proc_exec = []
    p1 = get_point(ats, point_x)
    proc_exec.append(p1.x)
    tpv = np.interp(p1.x, ats[0][0][0], ats[0][1].ravel())
    closest_point = Point(p1.x, tpv)
    line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
    for n in range(len(ats)-1):
        proc_exec.append(closest_point.x)
        p1 = closest_point
        tpv = np.interp(p1.x, ats[n+1][0][0], ats[n+1][1].ravel())
        closest_point = Point(p1.x, tpv)
        line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
        if n == len(ats)-2:
            proc_exec.append(closest_point.x)
    scaled_lengths = scale_lengths(line_segments, scale_factor)
    scaled_and_spaced_lengths = add_offset(scaled_lengths, offset)
    return scaled_and_spaced_lengths, line_segments, proc_exec

def cst_slope(x1, y1, x2, y2): 
    if(x2 - x1 != 0):
        return (float)(y2-y1)/(x2-x1)
    return sys.maxsize