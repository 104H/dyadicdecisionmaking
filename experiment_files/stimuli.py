# 15 May 2021


import numpy as np
from psychopy import visual


class stimulus:
    def __init__(self, X, window, xoffset):
        # the annulus is created by passing a matrix of zeros to the texture argument
        self.annulus = visual.GratingStim(
            win=window, mask='circle', tex=np.zeros((64, 64)), pos=[0 + xoffset, 0],
            size=50, contrast=1.0, opacity=1.0,
        )

        # noise patch
        self.noise = visual.NoiseStim(
            win=window, blendmode='add', mask='circle', pos=[0 + xoffset, 0],
            size=X, noiseElementSize=1, contrast=1.0, opacity=1.0,
            noiseType='Binary'
        )

        # red fixation dot for decision phase
        self.reddot = visual.GratingStim(
            win=window, size=5, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='red', mask='circle'
        )

        # green fixation dot for pre trial and inter trial condition
        self.greendot = visual.GratingStim(
            win=window, size=5, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='green', mask='circle'
        )
