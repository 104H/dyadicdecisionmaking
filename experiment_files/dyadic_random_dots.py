'''
    Naming Convention:
        The subjects are either refered to as 'sone' or 'stwo'
'''

import os
import sys
from subprocess import run
import numpy as np
import psychtoolbox as ptb
from psychopy import visual, event, core, gui, data, prefs, monitors
from psychopy.hardware import keyboard
import stimuli_random_dots as stimuli
import random as rn
import json

# # ''' REMOVED bc doesn't work ON WINDOWS
# import ctypes
# xlib = ctypes.cdll.LoadLibrary("libX11.so")
# xlib.XInitThreads()
# # '''


'''
    TO DO
    1. adjust fixation: correct size + correct colors
    2. different sounds for both participants
    3. make green/red -- right/left dependent on pair id
    4. display red text "too fast" if resp time <0.1s, or "too slow" if > 1.5s
    5. dotpatch: adjust size, speed, circle diameter, density (/pass correct parameters to dotstim method)
    6. make dots move as they're supposed to (see paper); right now they always move in the same direction
    7. feedback interval: replace dots with an isoluminant mask of stationary dots that were randomly distributed within the aperture of the 5° circle
            --- right now: dots just keep moving
    8. pretrial interval: same mask as in feedback interval (??? clarify)
            --- right now: dots just keep moving
    9. update instructions
    10. implement practice trials
    11. implement titration
'''


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
    #pair_id = int(sys.argv[1])
    pair_id = 10
except:
    print('Please enter a number as pair id as command-line argument!')
    sys.exit(-1)

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH * 2
M_HEIGHT = stimuli.M_HEIGHT
REFRESH_RATE = stimuli.REFRESH_RATE
N = stimuli.N

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=stimuli.distance)
myMon.setSizePix([M_WIDTH, M_HEIGHT])


window = visual.Window(size=(M_WIDTH, M_HEIGHT), monitor=myMon,
                       color="black", pos=(0,0), units='pix', blendMode='avg',
                       fullscr=False, allowGUI=False)

# window = visual.Window(size=(1000, 800), monitor=myMon,
#                        color="black", pos=(0,0), units='pix', blendMode='avg',
#                        fullscr=False, allowGUI=False)

window.mouseVisible = False # hide cursor
ofs = window.size[0] / 4

# update volume level of both speakers
#run(["amixer", "-D", "pulse", "sset", "Master", "30%,30%", "quiet"])

class subject:
    def __init__(self, sid, kb, buttonReverse=False):
        '''
            sid is 1 for chamber 1, and 2 for chamber 2

            kb is the psychopy keyboard object to connect to the button box
            keys is a list of keys expected from the user. it has to be in the order of yes and no
            state is either 0 or 1 for observing or do conditions, respectively
            xoffset is the constant added to all stimuli rendered for the subject
        '''

        # for now: right key = green (2, 7), left key = red (1, 8)

        keys = ["1", "2"] if sid == 1 else ["8", "7"]

        self.id = sid
        self.kb = kb
        self.state = False
        self.xoffset = ofs if sid == 1 else -ofs
        self.response = None

        soundclass = 'A' if sid == 1 else 'E'
        self.beep = Sound(soundclass, secs=0.5, volume=0.1)

        self.stimulus = stimuli.stim(window=window, xoffset=self.xoffset)

        if buttonReverse:
            self.buttons = {
                    keys[1] : "left",
                    keys[0] : "right",
                    None : "noresponse"
                    }
        else:
            self.buttons = {
                    keys[1] : "right",
                    keys[0] : "left",
                    None : "noresponse"
                    }

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

    def __repr__ (self):
        return str(self.id)



def getKeyboards():
    '''
        Search for the appropriate button box in each of the chambers
        Once a button has been pressed on each of the button boxes,
            create a keyboard object for each subject button box and assign it to them
    '''
    keybs = keyboard.getKeyboards()
    k = {"chone" : None, "chtwo" : None}

    for keyb in keybs:
        if keyb['product'] == "Black Box Toolkit Ltd. BBTK Response Box":
            if k['chone'] != None:
                k['chtwo'] = keyb['index']
                return k

            if k['chtwo'] != None:
                k['chone'] = keyb['index']
                return k

            ktemp = keyboard.Keyboard(keyb['index'])
            keypress = ktemp.waitKeys(keyList=["1", "2", "7", "8"])

            if keypress[0].name in ["1", "2"]:
                k['chone'] = keyb['index']
            else:
                k['chtwo'] = keyb['index']

if pair_id <= 13:
    ''' AT THE LAB:
    keybs = getKeyboards()
    sone = subject(1, keyboard.Keyboard( keybs["chone"] ),True)
    stwo = subject(2, keyboard.Keyboard( keybs["chtwo"] ),True)
    '''

    # if only one keyboard is connected (home testing)
    sone = subject(1, keyboard.Keyboard(), True)
    stwo = subject(2, keyboard.Keyboard(), True)
else:
    ''' AT THE LAB:
    keybs = getKeyboards()
    sone = subject(1, keyboard.Keyboard( keybs["chone"] ), False)
    stwo = subject(2, keyboard.Keyboard( keybs["chtwo"] ),False)
    '''

    # if only one keyboard is connected (home testing)
    sone = subject(1, keyboard.Keyboard(), False)
    stwo = subject(2, keyboard.Keyboard(), False)

subjects = [sone, stwo]

expkb = keyboard.Keyboard()

expinfo = {'pair': pair_id}

blocks = range(2)
ntrials = 4 # trials per block


#### FUNCTIONS TO CREATE DIFFERENT TEXT SCREENS #####
def gentext (instr):
    '''
        Generate text on both subject screens
    '''
    visual.TextStim(window,
                    text=instr, pos=[0 + sone.xoffset, 0],
                    color='white', height=20).draw()

    visual.TextStim(window,
                    text=instr, pos=[0 + stwo.xoffset, 0],
                    color='white', height=20).draw()

def genstartscreen ():
    instructions = "Welcome to our experiment! \n\n\
    X.\n\
    X.\n\n\
    Press the green key to continue"

    gentext(instructions)

def geninstructionspractice ():
    instructions = "Please read the instructions carefully.\n\
    X\n\n\
    Press yes to continue"

    gentext(instructions)

def geninstructionsexperiment ():
    instructions = "Now you’re ready to start the experiment. Please remember:\n\
    X\n\n\
    Press yes when you’re ready to start the experiment"

    gentext(instructions)

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


##### FUNCTIONS FOR THE TASK ITSELF #####
def drawStationaryDots(choice):
    '''
        draw the stationary dot patch for both subjects
    '''
    for s in subjects:
        s.stationarydotslist[choice].draw()


def drawMovingDots(subjects, choice, direction, frame):
    '''
        draw the moving dot patch for both subjects, but interleave three
        different dot patches
    '''
    if direction == 'right':
        for s in subjects:
            if frame == 0:
                s.movingrightdotslist[choice][0].draw()
            elif frame == 1:
                s.movingrightdotslist[choice][1].draw()
            elif frame == 2:
                s.movingrightdotslist[choice][2].draw()
            else:
                print('error in drawMovingDots function')
    else:
        for s in subjects:
            if frame == 0:
                s.movingleftdotslist[choice][0].draw()
            elif frame == 1:
                s.movingleftdotslist[choice][1].draw()
            elif frame == 2:
                s.movingleftdotslist[choice][2].draw()
            else:
                print('error in drawMovingDots function')


def drawFixation(color):
    '''
        draw the fixation crosses for both subjects
    '''
    if color == "green":
        for grating_one, grating_two in zip(sone.greencross, stwo.greencross):
            grating_one.draw()
            grating_two.draw()

    elif color == "yellow":
        for grating_one, grating_two in zip(sone.yellowcross, stwo.yellowcross):
            grating_one.draw()
            grating_two.draw()

    elif color == "blue":
        for grating_one, grating_two in zip(sone.bluecross, stwo.bluecross):
            grating_one.draw()
            grating_two.draw()

def genpretrialint (choice):
    drawFixation("green")
    drawStationaryDots(choice)

def gendecisionint (subjects, choice, direction, frame):
    drawFixation("green")
    drawMovingDots(subjects, choice, direction, frame)

def genfeedbackint (color, choice, rt_msg="NA"):
    '''
        1. Display static dot screen
        2. Response indicated by fixation dot color: left/ blue or right/ yellow (assignment depends on pair_id)
        3. The "do" subject sees response time message
    '''
    drawFixation(color)
    drawStationaryDots(choice)

    if rt_msg != "NA":
        if stwo.state:
            stwo.indicatordict[rt_msg].draw()
        else:
            sone.indicatordict[rt_msg].draw()

def fetchbuttonpress (subjects):
    '''
        Get the button box input from the acting subject
        Return the response (the pressed key) and the reaction time
    '''
    for s in subjects:
        if not s.state:
            continue
        else:
            temp = s.kb.getKeys(keyList=s.buttons.keys(), clear=True)

            if len(temp) == 0:
                resp = []
                s.response = s.buttons[None]
            else:
                keystroke = temp[0].name
                s.response = s.buttons[keystroke]
                resp = [s.buttons[keystroke], temp[0].rt]

    return resp

def updatestate ():
    '''
        Update whose turn it is
    '''
    sone.state = next(iterstates)
    stwo.state = bool(1 - sone.state)

def secondstoframes (seconds):
    return range( int( np.rint(seconds * REFRESH_RATE) ) )

def getacknowledgements ():
    '''
        Wait until both subjects have confirmed they are ready by pressing "yes"
    '''
    sone.kb.clearEvents(eventType="keyboard")
    stwo.kb.clearEvents(eventType="keyboard")
    key = []
    while not key:
        key = sone.kb.getKeys()

    sone.kb.clearEvents(eventType="keyboard")
    stwo.kb.clearEvents(eventType="keyboard")

    '''
    sone_ack, stwo_ack = None, None

    while (sone_ack != 'yes') or (stwo_ack != 'yes'):
        resp1 = sone.kb.getKeys(clear=False)
        resp2 = stwo.kb.getKeys(clear=False)

        if resp1:
            for r in resp1:
                if sone_ack != 'yes': sone_ack = sone.buttons[ r.name ]
        if resp2:
            for r in resp2:
                if stwo_ack != 'yes': stwo_ack = stwo.buttons[ r.name ]
    sone.kb.clearEvents(eventType="keyboard")
    stwo.kb.clearEvents(eventType="keyboard")
    '''

def getexperimenterack ():
    '''
        Wait for the experimenter input
            q: quit experiment (data is saved)
            space: continue
    '''

    key = []
    while not key:
        key = sone.kb.getKeys()

    '''
    keys = expkb.waitKeys(keyList=["q", "space"], clear=True)
    if "q" in keys: # exit experiment
        window.close()
        core.quit()
    '''

def genactingstates (trials):
    '''
        Randomly generate list including the subject states (act/ observe)
    '''
    return np.random.choice(a=[True, False], size=trials)


def genmovingstates (trials):
    '''
        Generates list that contains the movement direction of the moving
        dot patch (left/ right)
    '''
    movingstates = ['left'] * (trials//2) + ['right'] * (trials//2)
    return rn.sample(movingstates, len(movingstates))


# specifications of output file
_thisDir = os.path.dirname(os.path.abspath(__file__))
expName = 'DDM'
filename = _thisDir + os.sep + u'data/%s_pair%s_%s' % (expName, expinfo['pair'], data.getDateStr())

exphandler = data.ExperimentHandler(name=expName, extraInfo=expinfo, saveWideText=True, dataFileName=filename)


##################################
##### PRACTICE TRIALS  START #####
##################################

nPracticeTrials = 4
'''
practiceCoherence = 0.5
coherence of dotpatches is already at 0.5 from initialization
'''

# practice trials instructions

iterstates = iter(genactingstates(nPracticeTrials))
movingstates = iter(genmovingstates(nPracticeTrials))

for trialNumber in range(0, nPracticeTrials):

    # subject state update
    updatestate()
    flag = "NA"

    # whose turn it is defines which beep is played
    beep = sone.beep if sone.state == 1 else stwo.beep

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
    beep.play(when=nextflip)

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

    # if response[1] > 1500:
    #    flag = "slow"
    # elif response[1] < 100:
    #    flag = "fast"

    # make random choice for stationary dot patch that should be used
    stationaryChoice = np.random.randint(0, N)

    # feedback interval: display the fixation cross color based on the correctness of response & stationary dots for 0.7s
    for frame in secondstoframes(0.7):
        genfeedbackint(color, stationaryChoice, flag)
        window.flip()



################################
##### PRACTICE TRIALS  END #####
################################


###########################
##### TITRATION START #####
###########################
'''
    TBD
    1. One block of 200 trials of randomly interleaved dot coherences (0, 10, 20, 40 or 80% coherence, 40 trials each)
    2. calculate individual 85% accuracy threshold using the proportional-rate diffusion model
        - IF performance on this block is too poor for estimation of a reliable psychometric function
                (in paper: mean estimated dot coherence for 85% accuracy: 85.36 +- 17.5%)
                → stop testing and exclude subjects from analysis

'''
#########################
##### TITRATION END #####
#########################



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
    iterstates = iter(genactingstates(ntrials))
    movingstates = iter(genmovingstates(ntrials))

    # traverse through trials
    for trialNumber in range(0, ntrials):

        # subject state update
        updatestate()
        flag = "NA"

        # whose turn it is defines which beep is played
        beep = sone.beep if sone.state == 1 else stwo.beep

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
            for frame in secondstoframes( np.random.uniform(4.3, 5.8) ):
                genpretrialint(0)
                window.flip()
        else:
            for frame in secondstoframes( np.random.uniform(4.3, 5.8) ):
                genpretrialint(stationaryChoice)
                window.flip()

        sone.kb.clearEvents(eventType='keyboard')
        stwo.kb.clearEvents(eventType='keyboard')

        sone.kb.clock.reset()
        stwo.kb.clock.reset()

        # preparing time for next window flip, to precisely co-ordinate window flip and beep
        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)

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

        #if response[1] > 1500:
        #    flag = "slow"
        #elif response[1] < 100:
        #    flag = "fast"

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
