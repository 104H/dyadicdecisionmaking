# 15 May 2021


import numpy as np
from psychopy import visual

# monitor specs global variables
M_WIDTH = 1920
M_HEIGHT = 1200
REFRESH_RATE = 60

# Gabor patch global variables
CYCLES = 10  # required cycles for the whole patch
X = 395  # size of texture in pixels, needs to be to the power of 2!
sf = CYCLES/X

gabortexture = (
    visual.filters.makeGrating(res=X, cycles=X * sf) *
    visual.filters.makeMask(matrixSize=X, shape="circle", range=[0, 1])
)


class stim:
    def __init__(self, X, window, xoffset, threshold):

        # noise texture to use for the noise patch
        noiseTexture = np.random.rand(128, 128) * 2.0 - 1

        # custom trasparency mask for noise and signal
        gaussian_ann = np.load(open('experiment_files/gaussian-mask.npy', 'rb'))

        self.signal = visual.GratingStim(
            win=window, blendmode='add', tex='sin', mask=gaussian_ann, pos=[0 + xoffset, 0],
            size=X, sf=10/X, contrast=1.0, opacity=threshold,
        )

        # noise patch
        self.noise = visual.GratingStim(window, tex=noiseTexture,
            size=(395, 395), units='pix', mask = gaussian_ann,
            contrast=0.05, pos=[0 + xoffset, 0],
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
