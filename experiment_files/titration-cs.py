import sys
import os
import json
import time
import numpy as np
import pandas as pd
import psychopy
from psychopy import visual, event, core, monitors, data, prefs
from stimuli_random_dots import createDots
import stimuli_random_dots as stimuli
from psychopy.sound import Sound
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random


# set up sound for beeps
prefs.hardware['audioLib'] = ['PTB']

# Directory Specs
HOME = os.getcwd()
DATA = '/data/'

# Subject data dictionary
subjectData = {'pair_id': [], 'titration_counter': [], 'chamber':[], 'threshold': [], 'threshold_list': [], 'responses': [], 'method': 'constants' }

# monitoring the while loop with..
titration_over = False

# monitoring how often the titration has been done
titration_counter = 0

threshold = 0.1

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH
M_HEIGHT = stimuli.M_HEIGHT
N = stimuli.N
ndots = stimuli.ndots
dotlife = stimuli.dotlife
speed = stimuli.speed

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=80)
myMon.setSizePix([M_WIDTH, M_HEIGHT])

# create beep for decision interval
beep = Sound('A', secs=0.5, volume=0.1)

# get pair id via command-line argument
try:
    pair_id = int(sys.argv[1])
except:
    print('Please enter a number as pair id as command-line argument!')
    pair_id = input()

subjectData['pair_id'] = pair_id

def secondstoframes (seconds):
    REFRESH_RATE = 60
    return range( int( np.rint(seconds * REFRESH_RATE) ) )

def createDotPatch(window, xoffset, direction, coherence):
    stimList = []
    for _ in range(3):
        stimList.append(createDots(window, xoffset, direction, ndots//3, dotlife, speed, coherence))
    return stimList

def draw_fixation(fixation):
    for grating in fixation:
        grating.draw()

def drawDots(dotpatch):
    '''
        draw the dot patch
    '''
    dotpatch.draw()

def pretrial_interval(fixation, dotpatch):
    drawDots(dotpatch)
    draw_fixation(fixation)

def decision_interval(dotpatch):
    drawDots(dotpatch)
    draw_fixation(greencross)

def feedback_interval(fixation, dotpatch, indicatordict, rt_msg="NA"):
    '''
        1. Display static dot screen
        2. Correctness of response indicated by fixation dot color: correct/green,incorrect/light-red
        3. The "do" subject sees response time message
    '''
    drawDots(dotpatch)
    draw_fixation(fixation)

    # TODO: there is no indicatordict and no time measurement during titration
    if rt_msg != "NA":
        indicatordict[rt_msg].draw()

def endscreen():
    instructions = "You have finished the first part of the experiment."

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='white', height=20).draw()
# TODO:
def instruction_titration():
    instructions = "Please read the instructions carefully.\n\
    1. During the experiment, stay fixated on the dot in the center of the screen.\n\
    2. After the beep, you will see some dots moving either to the left or to the right. Hit the left (yellow) button if the dots are moving left, and the right (blue) button if the dots move right.\n\
    Press the right (blue) button to continue"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='white', height=20).draw()

# TODO:
def instruction_familiarization():
    instructions = "Welcome to our experiment!\n\n\
    Please read the instructions carefully.\n\
    1. During the experiment, stay fixated on the dot in the center of the screen.\n\
    2. After the beep, you will see some dots moving either to the left or to the right. Hit the left (yellow) button if the dots are moving left, and the right (blue) button if the dots move right.\n\
    Press the right (blue) button to start practice trials!11!1!"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='white', height=20).draw()

def get_threshold(intensities,responses):
    df = pd.DataFrame(intensities, columns = ['intensity'],dtype=float)
    df2 = pd.DataFrame(responses, columns = ['response'],dtype=float)
    df = pd.concat([df,df2],axis=1)
    df = df.groupby(['intensity'])['response'].mean().reset_index()
    fit = data.FitWeibull(df['intensity'], df['response'],expectedMin=0.5)
    smooth_intensities = np.linspace(min(intensities), max(intensities), 100)
    test_resp = fit.eval(smooth_intensities)
    threshold = fit.inverse(0.75)

    fig, ax = plt.subplots(1, 1)
    ax.plot(smooth_intensities, test_resp, '-')
    ax.axhline(0.75, linestyle='-', color='orange')
    ax.axvline(threshold, linestyle='-', color='orange')
    plt.title('threshold = %0.3f' % threshold)
    plt.plot(df['intensity'], df['response'], 'o')
    plt.ylim([0, 1])
    plt.savefig("data" + chamber + data.getDateStr() + '_psyfunc.jpg')

    return threshold

while titration_over == False:
    # input the chamber number in which titration takes place
    chamber = []
    if chamber == []:
        print("Enter chamber number (1 or 2):")
        chamber = input()

        if chamber not in ["1", "2"]:
            print("Wrong. Enter chamber number (1 or 2):")
            continue

    titration_counter += 1
    subjectData['titration_counter'] = titration_counter
    subjectData['chamber'] = chamber

    # variables for button box input
    keys = ["2", "1"] if chamber == "1" else ["7", "8"] # first one is right

    # the screen
    window = psychopy.visual.Window(size=(M_WIDTH, M_HEIGHT), units='pix', screen=int(chamber), fullscr=False, pos=None, color =[-1,-1,-1])
    window.mouseVisible = False # hide cursor
    xoffset = 0
    # the stimulus
    stimulus = stimuli.mainstim(window=window, xoffset=xoffset, coherence=0.5)
    stationaryDotsList = stimulus.stationaryDotsList
    stationaryDotPatch = stationaryDotsList[0]

    bluecross = stimulus.fixation_blue
    greencross = stimulus.fixation_green
    yellowcross = stimulus.fixation_yellow

    indicatordict = stimulus.indicatordict

    # '''
    # 1. Familiarization
    # '''

    instruction_familiarization() # display instructions
    window.flip()
    key = event.waitKeys(keyList=keys[:1])

    practice_trials = [0.05, 0.1, 0.2, 0.4, 0.8]*3
    random.shuffle(practice_trials)
    for coherence in practice_trials:

        # randomly pick dot motion direction and set coherence
        direction = np.random.choice(np.array([0, 180]))
        movingDotPatch = createDotPatch(window, xoffset, direction, coherence)
        key = []

        # pretrial interval
        for frame in secondstoframes( np.random.uniform(1, 2) ):
            # window.flip() #(for feedback)
            pretrial_interval(greencross, stationaryDotPatch)
            window.flip()

        # play beep because next is decision interval (beep should depend on chamber number)

        event.clearEvents()
        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)

        # decision interval: light blue cross & moving dots
        response = None  # we have no response yet
        for frame in secondstoframes(100):
            if frame % 3 == 0:
                decision_interval(movingDotPatch[0])
            elif frame % 3 == 1:
                decision_interval(movingDotPatch[1])
            elif frame % 3 == 2:
                decision_interval(movingDotPatch[2])
            else:
                print('error in secondstoframes decision_interval')
            window.flip()

            # fetch button press: response 0 is right, response 1 is left
            if response is None:
                #event.clearEvents()
                key = event.getKeys(keyList=keys)
                if keys[1] in key:
                    print("left")
                    response = 1

                elif keys[0] in key:
                    print("right")
                    response = 0

            else:

                if direction == 180:
                    print("true left")
                    direction_left = 1
                else:
                    print("true right")
                    direction_left = 0
                # check whether response and direction are matching and add to staircase
                if response == direction_left:
                    correct = 1
                    print("Good")
                else:
                    correct = 0
                break

        beep.stop()

        # randomly pick a stationary dot patch
        stationaryDotPatch = stationaryDotsList[np.random.randint(0, N)]

        # start feedback interval
        if response == 1: # left
            draw_fixation(yellowcross)
            drawDots(stationaryDotPatch)
            window.flip()
            core.wait(0.75)
        elif response == 0: #right
            draw_fixation(bluecross)
            drawDots(stationaryDotPatch)
            window.flip()
            core.wait(0.75)



    '''
    2. Titration
    '''
    # the contrast set to be tested
    # min_coherence = 0.01
    # max_coherence = 0.8
    #coherences = np.linspace(min_coherence, max_coherence, 5)
    coherences = [0.05, 0.1, 0.2, 0.4, 0.8] # this is taken from Murphy et al 2014
    thresholds = [{'coherence': c} for c in coherences]
    num_repetitions = 40

    # the trialhandler
    trials = data.TrialHandler(thresholds, num_repetitions, method='random')

    instruction_titration() # display instructions
    window.flip()
    key = event.waitKeys(keyList=keys[:1])

    """
    Main section
    """
    # list that is filled with the staircase values
    thresholds = []
    responses = []

    for trial in trials:

        # randomly pick dot motion direction and set coherence
        direction = np.random.choice(np.array([0, 180]))
        coherence = trial['coherence'] # update the coherence value
        thresholds.append(coherence)
        movingDotPatch = createDotPatch(window, xoffset, direction, coherence)
        key = []

        # pretrial interval
        for frame in secondstoframes( np.random.uniform(1, 2) ):
            # window.flip() #(for feedback)
            pretrial_interval(greencross, stationaryDotPatch)
            window.flip()

        # play beep because next is decision interval (beep should depend on chamber number)

        event.clearEvents()
        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)

        # decision interval: light blue cross & moving dots
        response = None  # we have no response yet
        for frame in secondstoframes(100):
            if frame % 3 == 0:
                decision_interval(movingDotPatch[0])
            elif frame % 3 == 1:
                decision_interval(movingDotPatch[1])
            elif frame % 3 == 2:
                decision_interval(movingDotPatch[2])
            else:
                print('error in secondstoframes decision_interval')
            window.flip()

            # fetch button press: response 0 is right, response 1 is left
            if response is None:
                #event.clearEvents()
                key = event.getKeys(keyList=keys)
                if keys[1] in key:
                    print("left")
                    response = 1

                elif keys[0] in key:
                    print("right")
                    response = 0

            else:

                if direction == 180:
                    print("true left")
                    direction_left = 1
                else:
                    print("true right")
                    direction_left = 0
                # check whether response and direction are matching and add to staircase
                if response == direction_left:
                    correct = 1
                    print("Good")
                else:
                    correct = 0

                responses.append(correct)
                break

        beep.stop()

        # randomly pick a stationary dot patch
        stationaryDotPatch = stationaryDotsList[np.random.randint(0, N)]

        # start feedback interval
        if response == 1: # left
            draw_fixation(yellowcross)
            drawDots(stationaryDotPatch)
            window.flip()
            core.wait(0.75)
        elif response == 0: #right
            draw_fixation(bluecross)
            drawDots(stationaryDotPatch)
            window.flip()
            core.wait(0.75)

    # fill subject dictionary with threshold and staircase value list
    subjectData['threshold_list'] = thresholds
    subjectData['responses'] = responses

    endscreen()
    window.flip()
    core.wait(5)
    window.close()

    titration_over = True
    # Create directory and save the responses
    DATAPATH = HOME + DATA + str(pair_id)
    if not os.path.exists(DATAPATH):
        os.makedirs(DATAPATH)
    os.chdir(DATAPATH)

    subjectData['threshold'] = get_threshold(thresholds,responses)
    with open('data_chamber' + chamber + '.json', 'w') as fp:
        json.dump(subjectData, fp)

    print("The participant's threshold is: " + str(subjectData['threshold']))
