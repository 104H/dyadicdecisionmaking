from stimuli_random_dots.py import M_WIDTH, M_WIDTH_CM, distance
from math import tan
import numpy as np


def degrees_to_pix(degrees):
    cm = tan(degrees * np.pi / 180) * distance
    pix = cm * M_WIDTH / M_WIDTH_CM
    return pix
