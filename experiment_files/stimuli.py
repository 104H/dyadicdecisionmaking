# 15 May 2021


import numpy as np
from psychopy import visual


class stimulus:
    def __init__(self, X, window, xoffset, threshold):

        self.signal = visual.GratingStim(
            win=window, blendmode='add', tex='sin', mask=gaussian_ann, pos=[0 + xoffset, 0],
            size=X, contrast=1.0, opacity=threshold,
        )

        # noise patch
        self.noise = visual.GratingStim(win, tex=noiseTexture,
            size=(395, 395), units='pix', mask = gaussian_ann,
            contrast=0.05,
            interpolate=False, autoLog=False)

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
