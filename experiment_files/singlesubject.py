# 10 April 2021

import os
import numpy as np
import psychtoolbox as ptb
from psychopy import visual, event, core, gui, data, sound
from psychopy.sound import Sound
from numpy.random import random

### Global variables for rendering stimuli
window = visual.Window(size=(1024,768), units='pix', fullscr=False)

blocks = range(3)
ntrials = 5
sthresh = 0.3 # contrast threshold for subject determined after titration
X = 512; # width of the gabor patch in pixels
sf = .02; # spatial frequency, cycles per pixel
noisetexture = random([X,X])*2.-1. # a X-by-X array of random numbers in [-1,1]


gabortexture = (
    visual.filters.makeGrating(res=X, cycles=X * sf) *
    visual.filters.makeMask(matrixSize=X, shape="circle", range=[0, 1])
)

# signal grating patch
signal = visual.GratingStim(
    win = window, tex = gabortexture, mask = 'circle',
    size = X, contrast = 1.0, opacity = sthresh,
)

# noise patch
# the annulus is created by passing a matrix of zeros to the texture argument
annulus = visual.GratingStim(
    win = window, mask='circle', tex=np.zeros((X,X)),
    size = 50, contrast = 1.0, opacity = 1.0,
)

# noise patch
noise = visual.RadialStim(
    win = window, mask='none', tex = noisetexture,
    size = X, contrast = 1.0, opacity = 1.0,
)

# red fixation dot for decision phase
reddot = visual.GratingStim(
    win = window, size=5, units='pix', pos=[0,0],
    sf=0, color='red', mask='circle'
)

# green fixation dot for pre trial and inter trial condition
greendot = visual.GratingStim(
    win = window, size=5, units='pix', pos=[0,0],
    sf=0, color='green', mask='circle'
)

beep = sound.Sound('A', secs=0.5)


def geninstruction (window):
    instructions = "Instructions:\n\
    Your task is to indicate if you see a vertical grating or not.\n\
    1. At the start of each trial, a red dot is shown in the middle of the screen.\n\
    2. When you hear a beep, you may press one of the buttons to indicate if you saw a vertical grating or not.\n\
    3. Press the left key for 'yes' and the right key for 'no'.\n\
    4. After a short break, the procedure will be repeated from step 1.\n\
    5. After 80 trials, you will have a break.\n\
    6. After the break, press the spacebar when ready to continue.\n\
    7. There will be a total of 6 blocks. \n\n\
    Press spacebar when ready."

    instructions = visual.TextStim(window,
                                    text=instructions,
                                    color='black', height=20)


def genbaseline (window):
    noise.draw(window)
    annulus.draw(window)
    reddot.draw(window)

def gendecisionint (window, condition):
    '''
        Generate the stimulus
        condition:
            's' for Signal
            'n' for Noise
    '''
    if condition == 'noise':
        genbaseline(window)
    elif condition == 'signal':
        noise.draw(window)
        signal.draw(window)
        annulus.draw(window)
        reddot.draw(window)
    else:
        raise("Please provide s for signal and n for noise in condition argument")

def genintertrial (window):
    noise.draw(window)
    annulus.draw(window)
    greendot.draw(window)

def genbreakscreen (window):
    '''
        Generate the screen shown when the break is in progress
    '''
    instructions = "Instructions:\n\
    Enjoy your break. Press any key to resume."

    instructions = visual.TextStim(window,
                                    text=instructions,
                                    color='black', height=20)

def genendscreen (nextcondition):
    '''
        Generate the end screen
        Args:
            nextcondition:
                'd' : Go to the dyadic condition
                'i' : Go to the individual condition
                'e' : End the experiment
    '''
    instructions = "Thank you for your time."

    instructions = visual.TextStim(window,
                                    text=instructions,
                                    color='black', height=20)


def fetchbuttonpress (connector):
    '''
        Looks for input from a pyserial connector
        Args:
            connector: PySerial object of connection to button box
    '''
    pass

def selectdyad ():
    '''
        Which dyad makes the button box
    '''
    pass


# generate file for storing data

# create trial handler
triallist = [
        {"condition": "signal", "correct_response": "a"},
        {"condition": "noise", "correct_response": "d"}
        ]

expinfo = {'participant': 'john doe', 'pair': 1}

trials = data.TrialHandler(triallist, nReps=ntrials, extraInfo=expinfo, method='random', originPath=-1)

for block in blocks:
    # traverse through trials
    for trial in trials:
        # display baseline
        genbaseline(window)
        window.flip()
        core.wait(2)

        # display stimulus
        gendecisionint(window, trials.thisTrial['condition'])
        window.flip()
        core.wait(2)

        # fetch button press
        fetchbuttonpress(None)

        # display inter trial interval
        genintertrial(window)
        window.flip()
        core.wait(2)

    # decide between continuing with next block, take a break

# write to file
print(trials.data)
