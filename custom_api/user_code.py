import numpy as np
from PIL import Image


#example functions
def test_func1(input):
    output = np.max(input) - input
    return output


def test_func2(input,min_v:int,max_v:int):
    output = input.astype(np.float32)
    output[output<min_v] = min_v
    output[output>max_v] = min_v
    output = (output - min_v)/(max_v - min_v) * 255
    output = output.astype(np.uint8)
    return output


def find_percentile_region(input,start_percent:float,end_percent:float):
    low_v = np.percentile(input, start_percent*100)
    high_v = np.percentile(input, end_percent*100)
    output = np.where((input >= low_v) & (input <= high_v), input, 0)
    return output
