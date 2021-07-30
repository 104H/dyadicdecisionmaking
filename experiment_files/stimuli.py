import numpy as np
from psychopy import visual
from numpy.random import random

# monitor specs global variables
M_WIDTH = 1920
M_HEIGHT = 1200
REFRESH_RATE = 60

# gabor patch global variables
X = 1024  # size of texture in pixels, needs to be a power of 2
CYCLES = 20
size=1024 # stimulus size in pixels
sf = CYCLES/size;

# custom transparency mask
with open('experiment_files/gaussian_ann.npy', 'rb') as f:
     gaussian = np.load(f)

mask_tex = np.interp(gaussian, (gaussian.min(), gaussian.max()), (0, 1))

mask = np.interp(gaussian, (gaussian.min(), gaussian.max()), (-1, 1))

noiseTexture = random([X**2]) * 2.0 - 1

gabortexture = (
    visual.filters.makeGrating(res=X, cycles= 20)
)

gabortexture = gabortexture * 0.1 * mask_tex


class stim:
    def __init__(self, window, xoffset, threshold):

        # noise patch
        self.noise = visual.GratingStim(
            win=window, tex=np.reshape(noiseTexture,(size,size)),
            mask=mask,
            size=size, units='pix',
            opacity=0.05, contrast=1
        )

        # signal
        self.signal = visual.GratingStim(
            win=window, tex=gabortexture, mask=mask, pos=[0 + xoffset, 0],
            size=size, contrast=1.0, opacity=threshold
        )

        # red fixation dot for baseline and decision interval
        self.reddot = visual.GratingStim(
            win=window, size=5, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='red', mask='circle', blendmode='avg'
        )

        # green fixation dot for inter trial condition
        self.greendot = visual.GratingStim(
            win=window, size=5, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='green', mask='circle', blendmode='avg'
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
        np.random.shuffle(noiseTexture)
        self.noise.tex = np.reshape(noiseTexture,(X,X))
