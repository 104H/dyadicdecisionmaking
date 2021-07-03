# 15 May 2021


import numpy as np
from psychopy import visual

# monitor specs global variables
M_WIDTH = 1920
M_HEIGHT = 1200
REFRESH_RATE = 60

# gabor patch global variables
X = 684  # size of texture in pixels, needs to be to the power of 2!

# custom gaussian mask
maskarray = np.load('maskarray.npy')

class stim:
    def __init__(self, window, xoffset, threshold):
        # noise patch
        self.noise = visual.GratingStim(
            win=window, mask=maskarray, ori=1.0, pos=[0 + xoffset, 0], blendmode='add', size=X,
            opacity=0.05, contrast=1, tex=np.random.rand(X, X) * 2.0 - 1
        )

        # signal
        self.signal = visual.GratingStim(
            win=window, blendmode='add', tex='sin', mask=maskarray, pos=[0 + xoffset, 0],
            size=X, sf=10 / X, contrast=1.0, opacity=threshold
        )

        # red fixation dot for baseline and decision interval
        self.reddot = visual.GratingStim(
            win=window, size=5, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='red', mask='circle'
        )

        # green fixation dot for inter trial condition
        self.greendot = visual.GratingStim(
            win=window, size=5, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='green', mask='circle'
        )

        # a dot which indicates to the subject they are in the observation state
        self.indicatordict = {
            "yes": visual.TextStim(
                win=window, text="Yes", units='pix', pos=[0 + xoffset, 0]
            ),
            "no": visual.TextStim(
                win=window, text="No", units='pix', pos=[0 + xoffset, 0]
            ),
            "noresponse": visual.TextStim(
                win=window, text="No Response", units='pix', pos=[0 + xoffset, 0]
            )
        }

    def updateNoise(self):
        self.noise.tex = np.random.rand(X, X) * 2.0 - 1