import numpy as np
from psychopy import visual

# monitor specs global variables
M_WIDTH = 1920
M_HEIGHT = 1200
REFRESH_RATE = 60

# gabor patch global variables
X = 2048  # size of texture in pixels, needs to be a power of 2
CYCLES = 20
size=1066
sf = CYCLES/size;

# custom transparency mask
with open('gaussian_ann.npy', 'rb') as f:
     gaussian_ann = np.load(f)

class stim:
    def __init__(self, window, xoffset, threshold):
        # noise patch
        self.noise = visual.GratingStim(
            win=window, mask=gaussian_ann, ori=1.0, pos=[0 + xoffset, 0], blendmode='add', size=size,
            opacity=0.05, contrast=1, tex=np.random.rand(X, X) * 2.0 - 1
        )

        # signal
        self.signal = visual.GratingStim(
            win=window, blendmode='add', tex='sin', mask=gaussian_ann, pos=[0 + xoffset, 0],
            size=size, sf=10 / size, contrast=1.0, opacity=threshold
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
