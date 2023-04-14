
from read_files import read
from static_outlier_detection import static_od
from dynamic_outlier_detection import dynamic_od
import os

def preprocess():
    absolute_path = os.path.dirname(__file__)
    relative_path = "data_set" 
    directory = os.path.join(absolute_path, relative_path)
    time_sequence, all_peinfo = read(directory) 
    window_size = 60
    max_group_size = 5
    ats, infoingroups = static_od(time_sequence, all_peinfo, window_size, max_group_size)
    # if its dynamic just directly call the dynamic thingy and skip preprocess, but remember to discretize, depending on how we receive the value
    # ats, infoingroups = dynamic_od(sensor_stream, window_size)
    return ats, infoingroups
