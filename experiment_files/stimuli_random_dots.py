from __future__ import division
from __future__ import print_function

from psychopy import visual, event, core
from random import choice
from math import tan, pi, atan

# monitor specs global variables
M_WIDTH = 1920
M_WIDTH_CM = 51.84
M_HEIGHT = 1200
REFRESH_RATE = 60

def degrees_to_pix(degrees):
    cm = tan(degrees * pi / 180) * distance
    pix = cm * M_WIDTH / M_WIDTH_CM
    return pix

my_dpi = 96 # dpi of the lab monitor
distance = 60 # distance to screen in cm
N = 25 # number of prepared dot patches

ndots = 328
dotlife = 5
speed = degrees_to_pix(5) / REFRESH_RATE
practiceTrialCoherence = 0.5


def pix_to_degrees(pix):
    conversion_factor = M_WIDTH_CM / M_WIDTH
    degrees = atan( (pix * conversion_factor) / distance)
    return degrees

def createDots (window, xoffset, dir, ndots, dotlife, speed, coherence):
    return visual.DotStim(
        window,
        color=(1.0, 1.0, 1.0),
        dir = dir,
        units='pix',
        nDots=ndots,
        fieldShape='circle',
        fieldPos=[0 + xoffset, 0],
        fieldSize=degrees_to_pix(10),
        dotLife=dotlife, # number of frames for each dot to be drawn
        signalDots='same',  # are signal dots 'same' on each frame? (see Scase et al)
        noiseDots='direction', # do the noise dots follow random- 'walk', 'direction', or 'position'
        speed=speed, #  degrees_to_pix(5) / REFRESH_RATE
        coherence=coherence # coherence of practice trials
    )


def createStationaryDots (N, window, xoffset, coherence):
    '''
        creates N different patches of randomly distributed stationary dots
    '''
    dotsList = []

    for _ in range(N):
        dotsList.append(createDots(window, xoffset, 0, ndots, -1, 0, coherence))

    return dotsList


def createMovingDots (N, window, xoffset, dir, coherence):
    '''
        creates 3xN different patches of randomly distributed moving dots
        3 patches are then used for the interleaving frames
    '''
    dots = []
    dotsList = []

    for _ in range(N):
        for count in range(3):
                dots.append(createDots(window, xoffset, dir, ndots//3, dotlife, speed, coherence))

        dotsList.append(dots)

    return dotsList
    

def createMovingDotsPractice (N, window, xoffset, dir, coherence):
    '''
        creates 3xN different patches of randomly distributed moving dots
        3 patches are then used for the interleaving frames
    '''
    dots = []
    dotsList = []

    for _ in range(N):
        for count in range(3):
                dots.append(createDots(window, xoffset, dir, ndots//3, dotlife, speed, coherence))

        dotsList.append(dots)

    return dotsList
    

def createFixation (window, xoffset, color):
    fixationList = [
        visual.GratingStim(
            win=window, size=21, units='pix', pos=[0 + xoffset, 0],
            sf=0, color=color, mask='circle'
        ),

        visual.GratingStim(
            win=window, size=25, units="pix",  pos=[0 + xoffset, 0],
            sf=0, color="black", mask="cross"
        ),

        visual.GratingStim(
            win=window, size=7, units='pix', pos=[0 + xoffset, 0],
            sf=0, color=color, mask='circle'
        )
    ]
    return fixationList


class mainstim:
    def __init__(self, window, xoffset, coherence):
        # list of differently distributed startionary dots
        self.stationaryDotsList = createStationaryDots(N, window, xoffset, 0)
        
        # lists of differently distributed moving dots (first for direction=0,
        # second for direction=180) for practice trials
        self.movingRightDotsListPractice = createMovingDotsPractice(N, window, xoffset, 0, practiceTrialCoherence)
        self.movingLeftDotsListPractice = createMovingDotsPractice(N, window, xoffset, 180, practiceTrialCoherence)

        # lists of differently distributed moving dots (first for direction=0,
        # second for direction=180) for main experiment
        self.movingRightDotsList = createMovingDots(N, window, xoffset, 0, coherence)
        self.movingLeftDotsList = createMovingDots(N, window, xoffset, 180, coherence)

        # fixation composite targets
        self.fixation_green = createFixation(window, xoffset, "darkgreen")
        self.fixation_blue = createFixation(window, xoffset, "darkblue")
        self.fixation_yellow = createFixation(window, xoffset, "yellow")

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
