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
N = 25 # number of prepared dot patches

dotlife = 5
speed = 2.5


def degrees_to_pix(degrees):
    cm = tan(degrees * pi / 180) * distance
    pix = cm * M_WIDTH / M_WIDTH_CM
    return pix


def createDots (window, xoffset, dir, dotlife, speed):
    return visual.DotStim(
        window,
        color=(1.0, 1.0, 1.0),
        dir = dir,
        units='pix',
        nDots=328,
        fieldShape='circle',
        fieldPos=[0 + xoffset, 0],
        fieldSize=degrees_to_pix(10),
        dotLife=dotlife, # number of frames for each dot to be drawn
        signalDots='same',  # are signal dots 'same' on each frame? (see Scase et al)
        noiseDots='direction', # do the noise dots follow random- 'walk', 'direction', or 'position'
        speed=speed,
        coherence=0.5 # coherence of practice trials
    )
    
    
def createStationaryDots (N, window, xoffset):
    '''
        creates N different patches of randomly distributed stationary dots
    '''
    dotsList = []

    for _ in range(N):
        dotsList.append(createDots(window, xoffset, 0, -1, 0))

    return dotsList
    

def createMovingDots (N, window, xoffset, dir):
    '''
        creates 3xN different patches of randomly distributed moving dots
        3 patches are then used for the interleaving frames
    '''
    dots = []
    dotsList = []

    for _ in range(N):
        for count in range(3):
                dots.append(createDots(window, xoffset, dir, dotlife, speed))

        dotsList.append(dots)

    return dotsList
    

class stim:
    def __init__(self, window, xoffset):
        #size of the fixation cross
        self.fixationSize = degrees_to_pix(0.36)
        
        # list of differently distributed startionary dots
        self.stationaryDotsList = createStationaryDots(N, window, xoffset)
        
        # lists of differently distributed moving dots (first for direction=0,
        # second for direction=180)
        self.movingRightDotsList = createMovingDots(N, window, xoffset, 0)
        self.movingLeftDotsList = createMovingDots(N, window, xoffset, 180)
        
        # TODO: this is still used for titration, the titration needs to be adapted
        self.dotPatch =  visual.DotStim(
            window,
            color=(1.0, 1.0, 1.0),
            dir = 0,
            units='pix',
            nDots=328,
            fieldShape='circle',
            fieldPos=[0 + xoffset, 0],
            fieldSize=degrees_to_pix(10),
            dotLife=dotlife, # number of frames for each dot to be drawn
            signalDots='same',  # are signal dots 'same' on each frame? (see Scase et al)
            noiseDots='direction', # do the noise dots follow random- 'walk', 'direction', or 'position'
            speed=speed,
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
