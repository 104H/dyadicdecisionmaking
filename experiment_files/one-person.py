import os
import sys
from subprocess import run
import numpy as np
import psychtoolbox as ptb
from psychopy import visual, event, core, gui, data, prefs, monitors
import stimuli_random_dots as stimuli
from random import choice, shuffle, sample
import json
import pandas as pd

'''
To obtain your sounddevices run the following line on the terminal
python3 -c "from psychopy.sound.backend_sounddevice import getDevices;print(getDevices())"
Copy the `name` attribute of your device to the audioDevice
'''

# setting PTB as our preferred sound library and then import sound
prefs.hardware['audioLib'] = ['PTB']

from psychopy import sound
sound.setDevice('USB Audio Device: - (hw:3,0)')

from psychopy.sound import Sound
from numpy.random import random

# get pair id via command-line argument
try:
    chamber_id = int(sys.argv[1])
except:
    print('Please enter a number as chamber id as command-line argument!')
    chamber_id = input()

#keys = ["1", "2"] if chamber_id == 1 else ["8", "7"] # 2 and 7 are green buttons (21.09.2021)

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH
M_HEIGHT = stimuli.M_HEIGHT
REFRESH_RATE = stimuli.REFRESH_RATE
N = stimuli.N

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=60)
myMon.setSizePix([M_WIDTH, M_HEIGHT])


window = visual.Window(size=(M_WIDTH, M_HEIGHT), color="black", monitor=myMon, units='pix', fullscr=False, allowGUI=False, pos=(0,0))
window.mouseVisible = False # hide cursor



class subject:
    def __init__(self, sid):
        '''
            sid is 1 for chamber 1, and 2 for chamber 2
            kb is the psychopy keyboard object to connect to the button box
            keys is a list of keys expected from the user. it has to be in the order of yes and no
            state is either 0 or 1 for observing or acting conditions, respectively
            threshold is the signal according to the subject's threshold
            xoffset is the constant added to all stimuli rendered for the subject
        '''

        # fetching subject titration thresholds
        #try:
        #    f = open("data/" + str(pair_id) + "/data_chamber" + str(sid) + ".json", "r")
        #    data = json.load(f)
        #except FileNotFoundError:
        #    print("Titration file not found for subject in chamber " + n)
        #    exit(-1)
        #else:
        #    self.threshold = data["threshold"]

        keys = ["1", "2"] if sid == 1 else ["8", "7"]
        self.buttons = {
                keys[1] : "left",
                keys[0] : "right",
                None : "noresponse"
                }

        self.id = sid
        self.response = None
        self.actingheadphonebalance = "30%,0%" if sid == 2 else "0%,30%"
        self.threshold = 0.095914589

        self.stimulus = stimuli.mainstim(window=window,xoffset=0,coherence=self.threshold)

        # stationary dot patches for pretrial and feedback phase
        self.stationarydotslist = self.stimulus.stationaryDotsList

        # moving dot patches for decision phase
        self.movingrightdotslist = self.stimulus.movingRightDotsList
        self.movingleftdotslist = self.stimulus.movingLeftDotsList

        # light blue fixation cross for decision phase
        self.bluecross = self.stimulus.fixation_blue

        # green fixation dot for feedback period (green = right)
        self.greencross = self.stimulus.fixation_green

        # red fixation dot for feedback period (red = left)
        self.yellowcross = self.stimulus.fixation_yellow

        # passing the response speed feedback to the stim object
        self.indicatordict = self.stimulus.indicatordict

        self.beep = Sound('A', secs=0.5, volume=0.1)

    def __repr__ (self):
        return str(self.id)

sone = subject(chamber_id)
subjects = [sone]
responsetime = core.Clock()

expinfo = {'chamber': chamber_id, 'threshold': sone.threshold}

blocks = range(2)
ntrials = 30 # trials per block

def secondstoframes (seconds):
    return range( int( np.rint(seconds * REFRESH_RATE) ) )


def fetchbuttonpress (subjects, clock):

    '''
    clock: PsychoPy clock object
    '''

    response = event.getKeys(timeStamped=clock, keyList=sone.buttons.keys())

    if len(response) == 0: response = [[None, 0]]
    return response

def gentext (instr):
    '''
        Generate text on both subject screens
    '''
    visual.TextStim(window,
                    text=instr, pos=[0, 0],
                    color='white', height=20).draw()


def genstartscreen ():
    instructions = "Welcome to our experiment! \n\n\
    X.\n\
    X.\n\n\
    Press the green key to continue"

    gentext(instructions)


def geninstructionspractice ():
    instructions = "Please read the instructions carefully.\n\
1. Place your index finger on the left key and your middle finger on the right key.\n\
2. Now, you will have a few practice trials to see how the experiment works.\n\
3. You will do the task together with your partner.\n\
4. The stimulus will be the same as you saw before: a set of moving dots.\n\
5. Press the blue key for left/right and the yellow key for left/right.\n\
6. It’s very important that you respond as quickly and as accurately as possible!\
Press blue/yellow to continue"

    gentext(instructions)

def geninstructionsexperiment ():
    instructions = "Now you’re ready to start the experiment. Please remember:\n\
1. Place your index finger on the left key and your middle finger on the right key.\n\
2. Fixate on the dot in the center.\n\
3. When you hear a beep a new trial has started. A high pitch beep is your queue to respond, a lower pitch beep means you have to observe your partner's reponse. \n\
4. Observe the movement of dots on the screen and determine their general direction.\
5. Press the blue key for left/right and the yellow key for left/right.\n\
6. Please respond as quickly and as accurately as possible! \n\
7. Once you've finished one block, you’ll be asked if you’re ready for the next block.\n\
8. After every second block, you will have a break.\n\
9. There will be a total of 12 blocks.\n\n\
Press yes when you’re ready to start the experiment"

    gentext(instructions)


def genmovingstates (trials):
    '''
        Generates list that contains the movement direction of the moving
        dot patch (left/ right)
    '''
    movingstates = ['left'] * (trials//2) + ['right'] * (trials//2)
    return sample(movingstates, len(movingstates))

def genendscreen ():
    instructions = "Thank you for your time.\n\n\
    Please let the experimenter know you're finished."

    gentext(instructions)

def genbreakscreen ():
    '''
        Generate the screen shown when the break is in progress
    '''
    instructions = "Are you ready for the next block?\n\n\
    Press yes when you're ready to resume"

    gentext(instructions)


def genmandatorybreakscreen ():
    '''
        Generate the screen shown when the mandatory break is in progress
    '''
    instructions = "Enjoy your break. Please inform the experimenter.\n\n\
    The experimenter will resume the experiment after a short break."

    gentext(instructions)

def genmovingstates (trials):
    '''
        Generates list that contains the movement direction of the moving
        dot patch (left/ right)
    '''
    movingstates = ['left'] * (trials//2) + ['right'] * (trials//2)
    return sample(movingstates, len(movingstates))


def drawStationaryDots(choice):
    '''
        draw the stationary dot patch for both subjects
    '''
    for s in subjects:
        s.stationarydotslist[choice].draw()

def drawFixation(color):
    '''
        draw the fixation crosses for both subjects
    '''
    if color == "green":
        for grating_one in sone.greencross:
            grating_one.draw()

    elif color == "yellow":
        for grating_one in sone.yellowcross:
            grating_one.draw()

    elif color == "blue":
        for grating_one in sone.bluecross:
            grating_one.draw()


def drawStationaryDots(choice):
    '''
        draw the stationary dot patch for both subjects
    '''
    for s in subjects:
        s.stationarydotslist[choice].draw()


def drawMovingDots(subjects, stimOne):
    '''
        draw the moving dot patch for both subjects, but interleave three
        different dot patches
    '''
    stimOne.draw()


def genfeedbackint (color, choice):
    '''
        1. Display static dot screen
        2. Response indicated by fixation dot color: left/ blue or right/ yellow (assignment depends on pair_id)
        3. The "do" subject sees response time message
    '''
    drawStationaryDots(choice)
    drawFixation(color)

def genpretrialint (choice):
    drawStationaryDots(choice)
    drawFixation("green")

def gendecisionint (subjects, stimOne):
    drawMovingDots(subjects, stimOne)
    drawFixation("green")

# specifications of output file
_thisDir = os.path.dirname(os.path.abspath(__file__))
expName = 'DDM'
filename = _thisDir + os.sep + u'data/%s_pair%s_%s' % (expName, expinfo['chamber'], data.getDateStr())

#triallist = [{"condition": "signal"}, {"condition": "noise"}] * (ntrials//2)

exphandler = data.ExperimentHandler(name=expName, extraInfo=expinfo, saveWideText=True, dataFileName=filename)

##### PRACTICE TRIALS  START #####

##### PRACTICE TRIALS  END #####

##### MAIN EXPERIMENT START #####

# display instructions for experiment
# start main experiment
for blockNumber in blocks:

    # make an iterator object
    movingstates = iter(genmovingstates(ntrials))
    nCorrect = nLeftCorrect = 0

    # traverse through trials
    for trialNumber in range(0, ntrials):


        # whose turn it is defines which beep is played
        beep = sone.beep

        # make random choice for moving dot patches that should be used and determine the direction
        dotpatchChoice = np.random.randint(0, N)
        movingDirection = next(movingstates)

        # save trial data to file
        exphandler.addData('block', blockNumber)
        exphandler.addData('trial', trialNumber)
        exphandler.addData('direction', movingDirection)

        # pretrial interval: display green fixation cross & stationary dots for 1 - 2 s (uniformly distributed)
        if trialNumber == 0:
            for frame in secondstoframes( np.random.uniform(1, 2) ):
                genpretrialint(0)
                window.flip()
        else:
            for frame in secondstoframes( np.random.uniform(1, 2) ):
                genpretrialint(stationaryChoice)
                window.flip()


        event.clearEvents()

        # preparing time for next window flip, to precisely co-ordinate window flip and beep
        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)
        # display stimulus
        responsetime.reset()

        # decision interval: cross & moving dots
        response = [[None, 0]]

        if movingDirection == 'right':
            stimOne = sone.movingrightdotslist[dotpatchChoice]
        else:
            stimOne = sone.movingleftdotslist[dotpatchChoice]

        for frame in secondstoframes(100):
            if frame % 3 == 0:
                gendecisionint(subjects, stimOne[0])
            elif frame % 3 == 1:
                gendecisionint(subjects, stimOne[1])
            elif frame % 3 == 2:
                gendecisionint(subjects, stimOne[2])
            else:
                print('error in secondstoframes gendecisionint')
            window.flip()

            # fetch button press
            if response[0][0] is None:
                response = fetchbuttonpress(sone, responsetime)
            else:
                break

        # need to explicity call stop() to go back to the beginning of the track
        beep.stop()

        # feedback interval (0.7s): color of fixation cross depends on response
        if not response[0][0]:
            color = "green"
        elif response[0][0] == "1":  # left
            color = "yellow"
            if movingDirection == "left":
                nCorrect += 1
                nLeftCorrect += 1
        elif response[0][0] == "2":  # right
            color = "blue"
            if movingDirection == "right":
                nCorrect += 1


        # make random choice for stationary dot patch that should be used
        stationaryChoice = np.random.randint(0, N)

        # feedback interval: display the fixation cross color based on the correctness of response & stationary dots for 0.7s
        for frame in secondstoframes(0.7):
            genfeedbackint(color, stationaryChoice)
            window.flip()

        # save response to file
        if not response:
            exphandler.addData('response', "noresponse")
            exphandler.addData('rt', "None")
        else:
            exphandler.addData('response', response[0][0])
            exphandler.addData('rt', response[0][1])

        # move to next row in output file
        exphandler.nextEntry()

    # after every second block (unless after the last block), there will be a mandatory break which only the experimenter can end
    if blockNumber % 2 == 0 and blockNumber != (blocks[-1]):
        genmandatorybreakscreen()
        window.flip()
        core.wait(4)
    # otherwise, wait for the subjects to start their next block
    else:
        genbreakscreen()
        window.flip()
        continue

genendscreen()
window.flip()
core.wait(5)

#code to calculate and show the performance metrics
print("Overall Accuracy: {0:<5.2%}".format( nCorrect/ntrials))
print("Left Accuracy   : {0:<5.2%}".format(2 * nLeftCorrect/ntrials))
print("Right Accuracy  : {0:<5.2%}".format(2 * (nCorrect - nLeftCorrect)/ntrials))
