from __future__ import division
from __future__ import print_function

from psychopy import visual, event, core
from random import choice
from math import tan, pi

# monitor specs global variables
M_WIDTH = 1920
M_WIDTH_CM = 51.84
M_HEIGHT = 1200
REFRESH_RATE = 60

my_dpi = 96 # dpi of the lab monitor
distance = 60 # distance to screen in cm

def degrees_to_pix(degrees):
    cm = tan(degrees * pi / 180) * distance
    pix = cm * M_WIDTH / M_WIDTH_CM
    return pix
    
N = 25
fsize = degrees_to_pix(10)
dotsSpeed = 2.5
dotsNumber = 328
    
    
def createStationaryDots (N, window, xoffset):
    '''
        creates N different patches of randomly distributed stationary dots
    '''
    dotsList = []

    for _ in range(N):
        tempDots = visual.DotStim(
            window,
            color=(1.0, 1.0, 1.0),
            units='pix',
            nDots=dotsNumber,
            fieldShape='circle',
            fieldPos=[0 + xoffset, 0],
            fieldSize=fsize,
            dotLife=-1,
            speed=0
        )

        dotsList.append(tempDots)

    return dotsList
    

class stim:
    def __init__(self, window, xoffset):
        #size of the fixation cross
        self.fixationSize = degrees_to_pix(0.36)
        
        # list of differently distributed stationary dots
        self.dotsList = createStationaryDots(N, window, xoffset)
        
        # stationary dot patch
        self.stationaryDotPatch = self.dotsList[0]
        
        # dot patch
        self.movingDotPatch = visual.DotStim(
            window,
            color=(1.0, 1.0, 1.0),
            dir=180,
            units='pix',
            nDots=dotsNumber,
            fieldShape='circle',
            fieldPos=[0 + xoffset, 0],
            fieldSize=fsize,
            dotLife=5,  # number of frames for each dot to be drawn
            signalDots='same',  # are signal dots 'same' on each frame? (see Scase et al)
            noiseDots='direction', # do the noise dots follow random- 'walk', 'direction', or 'position'
            speed=dotsSpeed,
            coherence=0.9
        )

        # light blue fixation cross for pretrial & decision interval
        self.bluecross = visual.GratingStim(
            win=window, size=self.fixationSize, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='blue', mask='cross'
        )

        # red fixation cross for feedback interval
        self.redcross = visual.GratingStim(
            win=window, size=self.fixationSize, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='red', mask='cross'
        )

        # green fixation cross for feedback interval
        self.greencross = visual.GratingStim(
            win=window, size=self.fixationSize, units='pix', pos=[0 + xoffset, 0],
            sf=0, color='green', mask='cross'
        )
        
        """
        For response time related warning to be shown on top of fixation cross
        a. if response time < 100 ms: Too Fast
        b. response time > 1500 ms: Too Slow
        """
        self.indicatordict = {
            "slow": visual.TextStim(
                win=window, text="Too Slow", units='pix', pos=[0 + xoffset, 0], color='red'
            ),
            "fast": visual.TextStim(
                win=window, text="Too Fast", units='pix', pos=[0 + xoffset, 0], color='red'
            )
        }
        
    def updateStationaryDots(self):
        return choice(self.dotsList)
