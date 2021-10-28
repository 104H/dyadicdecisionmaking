import os
import sys
from subprocess import run
import numpy as np
from numpy.random import random
import psychtoolbox as ptb
from psychopy import visual, event, core, gui, data, prefs, monitors
from psychopy.hardware import keyboard
import stimuli_random_dots as stimuli
from dyadic_random_dots import *
import random as rn
import json

# # ''' REMOVED bc doesn't work ON WINDOWS
# import ctypes
# xlib = ctypes.cdll.LoadLibrary("libX11.so")
# xlib.XInitThreads()
# # '''

# setting PTB as our preferred sound library and then import sound
prefs.hardware['audioLib'] = ['PTB']

from psychopy import sound
sound.setDevice('USB Audio Device: - (hw:3,0)')

from psychopy.sound import Sound

# update volume level of both speakers
#run(["amixer", "-D", "pulse", "sset", "Master", "30%,30%", "quiet"])

# get pair id via command-line argument
try:
    #pair_id = int(sys.argv[1])
    pair_id = 10
except:
    print('Please enter a number as pair id as command-line argument!')
    sys.exit(-1)

# get chamber number
chamber = []
while not chamber:
    if not chamber:
        print("Enter chamber number (1 or 2):")
        #chamber = input()
        chamber = "1"

        if chamber not in ["1", "2"]:
            print("Wrong. Enter chamber number (1 or 2):")
            continue


# monitor specs global variables
REFRESH_RATE = stimuli.REFRESH_RATE
N = stimuli.N

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=stimuli.distance)
myMon.setSizePix([M_WIDTH, M_HEIGHT])

ofs = 0

window = visual.Window(monitor=myMon,
                       color="black", pos=(0,0), units='pix', blendMode='avg', # have to use 'avg' to avoid artefacts
                       fullscr=False, allowGUI=False)

window.mouseVisible = False # hide cursor

if int(chamber) == 1:
    if pair_id <= 13:
        ''' AT THE LAB:
        keybs = getKeyboards()
        sone = subject(1, keyboard.Keyboard( keybs["chone"] ),True)
        '''
        # if only one keyboard is connected (home testing)
        sone = subject(1, keyboard.Keyboard(), True)
    else:
        ''' AT THE LAB:
        keybs = getKeyboards()
        sone = subject(1, keyboard.Keyboard( keybs["chone"] ), False)
        '''
        sone = subject(1, keyboard.Keyboard(), False)

    subjects = [sone]
    sone.state = True

else:
    if pair_id <= 13:
        ''' AT THE LAB:
        keybs = getKeyboards()
        stwo = subject(2, keyboard.Keyboard( keybs["chtwo"] ),True)
        '''
        # if only one keyboard is connected (home testing)
        stwo = subject(2, keyboard.Keyboard(), True)
    else:
        ''' AT THE LAB:
        keybs = getKeyboards()
        stwo = subject(2, keyboard.Keyboard( keybs["chtwo"] ),False)
        '''
        stwo = subject(2, keyboard.Keyboard(), False)

    subjects = [stwo]
    stwo.state = True


expkb = keyboard.Keyboard()

expinfo = {'pair': pair_id, 'chamber': chamber}

blocks = range(1)
ntrials = 2 # trials per block

# specifications of output file
_thisDir = os.path.dirname(os.path.abspath(__file__))
expName = 'DDM_single'
filename = _thisDir + os.sep + u'data/%s_pair%s_%s' % (expName, expinfo['pair'], data.getDateStr())

exphandler = data.ExperimentHandler(name=expName, extraInfo=expinfo, saveWideText=True, dataFileName=filename)

##################################
##### PRACTICE TRIALS  START #####
##################################

nPracticeTrials = 2
nCorrect = 0

# practice trials instructions
movingstates = iter(genmovingstates(nPracticeTrials))

for trialNumber in range(0, nPracticeTrials):

    flag = "NA"

    # pretrial interval: display light blue fixation cross & stationary dots for 4.3 - 5.8s (uniformly distributed)
    if trialNumber == 0:
        for frame in secondstoframes(np.random.uniform(4.3, 5.8)):
            genpretrialint(0)
            window.flip()
    else:
        for frame in secondstoframes(np.random.uniform(4.3, 5.8)):
            genpretrialint(stationaryChoice)
            window.flip()

    sone.kb.clearEvents(eventType='keyboard')
    stwo.kb.clearEvents(eventType='keyboard')

    sone.kb.clock.reset()
    stwo.kb.clock.reset()

    # preparing time for next window flip, to precisely co-ordinate window flip and beep
    nextflip = window.getFutureFlipTime(clock='ptb')
    subjects[0].beep.play(when=nextflip)

    # make random choice for stationary dot patches that should be used
    dotpatchChoice = np.random.randint(0, N)
    movingDirection = next(movingstates)

    # decision interval: light blue cross & moving dots
    response = []  # we have no response yet
    for frame in secondstoframes(3):
        # for frame in secondstoframes(1.5):
        if frame % 3 == 0:
            gendecisionint(subjects, dotpatchChoice, movingDirection, 0)
        elif frame % 3 == 1:
            gendecisionint(subjects, dotpatchChoice, movingDirection, 1)
        elif frame % 3 == 2:
            gendecisionint(subjects, dotpatchChoice, movingDirection, 2)
        else:
            print('error in secondstoframes gendecisionint')
        window.flip()

        # fetch button press
        if not response:
            response = fetchbuttonpress(subjects)
        else:
            break

    # need to explicity call stop() to go back to the beginning of the track
    beep.stop()

    # feedback interval (0.7s): color of fixation cross depends on response

    if not response:
        color = "green"
    elif response[0] == "left":  # left
        color = "yellow"
    elif response[0] == "right":  # right
        color = "blue"

    if response:
        if response[0] == movingDirection:  # correct response
            nCorrect += 1
        if response[1] > 1.5:
            flag = "slow"
        elif response[1] < 0.1:
            flag = "fast"

    # make random choice for stationary dot patch that should be used
    stationaryChoice = np.random.randint(0, N)

    # feedback interval: display the fixation cross color based on the correctness of response & stationary dots for 0.7s
    for frame in secondstoframes(0.7):
        genfeedbackint(color, stationaryChoice, flag)
        window.flip()

# Print correctness on the terminal for Practice Trials
print("{0:*>31s} {1:<5.2%}".format('Practice Trials Correct: ',nCorrect/nPracticeTrials))

################################
##### PRACTICE TRIALS  END #####
################################

#################################
##### MAIN EXPERIMENT START #####
#################################

# display instructions for experiment
geninstructionsexperiment()
window.flip()
getacknowledgements()

# start main experiment
for blockNumber in blocks:

    # make an iterator object
    movingstates = iter(genmovingstates(ntrials))

    # traverse through trials
    for trialNumber in range(0, ntrials):

        flag = "NA"

        # make random choice for moving dot patches that should be used and determine the direction
        dotpatchChoice = np.random.randint(0, N)
        movingDirection = next(movingstates)

        # save trial data to file
        exphandler.addData('block', blockNumber)
        exphandler.addData('trial', trialNumber)
        exphandler.addData('s1_state', sone.state)
        exphandler.addData('direction', movingDirection)

        # pretrial interval: display green fixation cross & stationary dots for 4.3 - 5.8s (uniformly distributed)
        if trialNumber == 0:
            for frame in secondstoframes(np.random.uniform(4.3, 5.8)):
                genpretrialint(0)
                window.flip()
        else:
            for frame in secondstoframes(np.random.uniform(4.3, 5.8)):
                genpretrialint(stationaryChoice)
                window.flip()

        sone.kb.clearEvents(eventType='keyboard')
        stwo.kb.clearEvents(eventType='keyboard')

        sone.kb.clock.reset()
        stwo.kb.clock.reset()

        # preparing time for next window flip, to precisely co-ordinate window flip and beep
        nextflip = window.getFutureFlipTime(clock='ptb')
        subjects[0].beep.play(when=nextflip)

        # decision interval: light blue cross & moving dots
        response = []  # we have no response yet
        for frame in secondstoframes(1.5):
            if frame % 3 == 0:
                gendecisionint(subjects, dotpatchChoice, movingDirection, 0)
            elif frame % 3 == 1:
                gendecisionint(subjects, dotpatchChoice, movingDirection, 1)
            elif frame % 3 == 2:
                gendecisionint(subjects, dotpatchChoice, movingDirection, 2)
            else:
                print('error in secondstoframes gendecisionint')
            window.flip()

            # fetch button press
            if not response:
                response = fetchbuttonpress(subjects)
            else:
                break

        # need to explicity call stop() to go back to the beginning of the track
        beep.stop()

        # feedback interval (0.7s): color of fixation cross depends on response

        if not response:
            color = "green"
        elif response[0] == "left":  # left
            color = "yellow"
        elif response[0] == "right":  # right
            color = "blue"

        """
        if response[1] > 1.5:
            flag = "slow"
        elif response[1] < 0.1:
            flag = "fast"
        """

        # make random choice for stationary dot patch that should be used
        stationaryChoice = np.random.randint(0, N)

        # feedback interval: display the fixation cross color based on the correctness of response & stationary dots for 0.7s
        for frame in secondstoframes(0.7):
            genfeedbackint(color, stationaryChoice, flag)
            window.flip()

        # save response to file
        if not response:
            exphandler.addData('response', "noresponse")
            exphandler.addData('rt', "None")
        else:
            exphandler.addData('response', response[0])
            exphandler.addData('rt', response[1])

        # move to next row in output file
        exphandler.nextEntry()

    # after every second block (unless after the last block), there will be a mandatory break which only the experimenter can end
    if blockNumber % 2 == 0 and blockNumber != (blocks[-1]):
        genmandatorybreakscreen()
        window.flip()
        getexperimenterack()
    # otherwise, wait for the subjects to start their next block
    else:
        genbreakscreen()
        window.flip()
        getacknowledgements()
        continue

genendscreen()
window.flip()
core.wait(10)

################################
###### MAIN EXPERIMENT END #####
################################
