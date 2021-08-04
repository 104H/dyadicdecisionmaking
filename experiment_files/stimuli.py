# 4 August 2021

import numpy as np
from math import tan, ceil
from psychopy import visual
from random import choice

# monitor specs global variables
M_WIDTH = 1920
M_WIDTH_CM = 51.84
M_HEIGHT = 1200
REFRESH_RATE = 60

# custom gaussian mask
maskarray = np.load('maskarray.npy')

# size of stimulus
X = maskarray.shape[0]

N = 25 # how many noise object with random textures should be created

# create custom texture for the signal
mask_tex = np.interp(maskarray, (maskarray.min(), maskarray.max()), (0, 1))
gabortexture = visual.filters.makeGrating(res=X, cycles=40) * 0.1 * mask_tex

def createNoise (X, N, window, xoffset):
    '''
        create N random noise textures of size X, pad them, create noise objects, and add those to a list
            why not just create an array with the textures?
            -> since texture rendering takes a lot of time, we need to create the noise objects beforehand
    '''

    noiseList = []

    for _ in range(N):
        # create random noise texture
        temp = np.random.rand(X, X) * 2.0 - 1

        # create noise object
        tempNoise = visual.GratingStim(
            win=window, mask=maskarray, ori=1.0, pos=[0 + xoffset, 0], blendmode='add', size=X,
            opacity=0.1, contrast=1, tex=temp
        )

        # add noise object to list
        noiseList.append(tempNoise)

    return noiseList


class stim:
    def __init__(self, window, xoffset, threshold):
        # list with noise objects
        self.noiseList = createNoise(X, N, window, xoffset)

        # noise patch
        self.noise = self.noiseList[0]

        # signal
        self.signal = visual.GratingStim(
            win=window, tex=gabortexture, mask=maskarray, pos=[0 + xoffset, 0],
            size=X, contrast=1.0, opacity=threshold
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

        # response from the other subject to be shown on top of the fixation dot
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
