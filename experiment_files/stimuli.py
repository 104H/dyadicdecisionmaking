import numpy as np
from psychopy import visual
from numpy.random import random
from random import choice

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

gabortexture = (
    visual.filters.makeGrating(res=X, cycles= 20)
)

gabortexture = gabortexture * 0.08 * mask_tex

N = 25 # how many random noise textures should be created

def createNoise (X, N, window, xoffset):
    '''
        create N random noise textures of size X, pad them, create noise objects, and add those to a list
            why not just create an array with the textures?
            -> since texture rendering takes a lot of time, we need to create the noise objects beforehand
    '''

    noiseList = []

    for _ in range(N):
        # create random noise texture
        temp = random([X,X]) * 2.0 - 1

        # create noise object
        tempNoise = visual.GratingStim(
            win=window, mask=mask, ori=1.0, pos=[0 + xoffset, 0], blendmode='add', size=X,
            opacity=0.1, contrast=1, tex=temp
        )

        # add noise object to list
        noiseList.append(tempNoise)

    return noiseList


class stim:
    def __init__(self, window, xoffset, threshold):

        # noise
        self.noiseList = createNoise(X, N, window, xoffset)

        self.noise = choice(self.noiseList)

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
        return choice(self.noiseList)
