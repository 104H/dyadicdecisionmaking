# 15 May 2021


import numpy as np
from psychopy import visual

# monitor specs global variables
M_WIDTH = 1920
M_HEIGHT = 1200
REFRESH_RATE = 60

# Gabor patch global variables
X = 512  # size of texture in pixels, needs to be to the power of 2!


class stim:
    def __init__(self, window, xoffset, threshold):

        self.noise = visual.NoiseStim(
            win=window, mask='gauss', ori=1.0, pos=[0 + xoffset, 0], blendmode='add', size=X, sf=None,
            phase=0, color=[1, 1, 1], colorSpace='rgb', opacity=1, contrast=1, filter='none',
            noiseType='Binary', noiseElementSize=1
        )

        self.donutmaker = visual.GratingStim(
            win=window, color='grey', tex=np.ones((X, X)), mask='gauss',
            size=X, contrast=1, opacity=1, pos=[0 + xoffset, 0]
        )

        self.signal = visual.GratingStim(
            win=window, blendmode='add', tex='sin', mask='gauss', pos=[0 + xoffset, 0],
            size=X, sf=10 / X, contrast=1.0, opacity=threshold
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
        
        # a dot which indicates to the subject they are in the observation state
        self.indicatordict = {
                "yes" : visual.TextStim(
                            win = window, text="Yes", units='pix', pos=[0 + xoffset, 0]
                        ),
                "no" : visual.TextStim(
                            win = window, text="No", units='pix', pos=[0 + xoffset, 0]
                        ),
                "noresponse" : visual.TextStim(
                            win = window, text="No Response", units='pix', pos=[0 + xoffset, 0]
                        )
                }

