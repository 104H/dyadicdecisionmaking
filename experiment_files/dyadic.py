# 11 April 2021

'''
    Naming Convention:
        The subjects are either refered to as 'sone' or 'stwo'
'''

import ctypes
#xlib = ctypes.cdll.LoadLibrary("libX11.so")
#xlib.XInitThreads()

import os
import sys
from subprocess import run
import numpy as np
import psychtoolbox as ptb
from psychopy import visual, event, core, gui, data, prefs, monitors
from psychopy.hardware import keyboard
import stimuli
from random import choice, shuffle
import json

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
    pair_id=2
    #pair_id = int(sys.argv[1])
except:
    print('Please enter a number as pair id as command-line argument!')
    sys.exit(-1)

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH * 2
M_HEIGHT = stimuli.M_HEIGHT
REFRESH_RATE = stimuli.REFRESH_RATE

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=65)


window = visual.Window(size=(M_WIDTH, M_HEIGHT), monitor=myMon, units='pix', blendMode='add', fullscr=False, useFBO=True, allowGUI=False, pos=(0,0))
window.mouseVisible = False # hide cursor
ofs = window.size[0] / 4

class subject:
    def __init__(self, sid, kb):
        '''
            sid is 1 for chamber 1, and 2 for chamber 2

            kb is the psychopy keyboard object to connect to the button box
            keys is a list of keys expected from the user. it has to be in the order of yes and no
            state is either 0 or 1 for observing or acting conditions, respectively
            threshold is the signal according to the subject's threshold
            xoffset is the constant added to all stimuli rendered for the subject
        '''

        keys = ["1", "2"] if sid == 1 else ["8", "7"]
        '''
        # fetching subject titration thresholds
        try:
            f = open("data/" + str(pair_id) + "/data_chamber" + str(sid) + ".json", "r")
            data = json.load(f)
        except FileNotFoundError:
            print("Titration file not found for subject in chamber " + n)
            exit(-1)
        else:
            self.threshold = data["threshold"]
        '''
        self.threshold = 0.01
        self.id = sid
        self.kb = kb
        self.state = False
        self.xoffset = ofs if sid == 1 else -ofs
        self.response = None
        self.actingheadphonebalance = "30%,0%" if sid == 2 else "0%,30%"

        stimulus = stimuli.stim(window=window, xoffset=self.xoffset, threshold=self.threshold)

        self.buttons = {
                    keys[1] : "yes",
                    keys[0] : "no",
                    None : "noresponse"
                    }

        # signal
        self.signal = stimulus.signal

        # noise patch
        self.noise = stimulus.noise

        # red fixation dot for decision phase
        self.reddot = stimulus.reddot

        # green fixation dot for pre trial and inter trial condition
        self.greendot = stimulus.greendot

        # a dot which indicates to the subject they are in the observation state
        self.indicatordict = stimulus.indicatordict

    def __repr__ (self):
        return str(self.id)



def getKeyboards():
    '''
        Search for the appropriate button box in each of the chambers
        Create a keyboard object for each subject button box and assign it to them

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
    '''
    pass

#keybs = getKeyboards()
kbone = keyboard.Keyboard()

sone = subject(1, kbone)
stwo = subject(2, kbone)
subjects = [sone, stwo]

expkb = keyboard.Keyboard()

expinfo = {'pair': pair_id}

blocks = range(2)
ntrials = 80 # trials per block

# create beep for decision interval
beep = Sound('A', secs=0.5, volume=0.1)

def gentext (instr):
    '''
        Generate text on both subject screens
    '''
    visual.TextStim(window,
                    text=instr, pos=[0 + sone.xoffset, 0],
                    color='black', height=20).draw()

    visual.TextStim(window,
                    text=instr, pos=[0 + stwo.xoffset, 0],
                    color='black', height=20).draw()

def genstartscreen ():
    instructions = "Welcome to our experiment! \n\n\
    Your task is to indicate whether you see a vertical grating or not.\n\
    If you have any questions after reading the instructions on the next screen, please feel free to ask the experimenter.\n\n\
    Press the green key to continue"

    gentext(instructions)

def geninstructionspractice ():
    instructions = "Please read the instructions carefully.\n\
    1. Place your index finger on the left key and your middle finger on the right key.\n\
    2. Now, you will have a few practice trials to see how the experiment works.\n\
    3. You will do the task together with your partner.\n\
    4. The stimulus will be the same as you saw before: a circle of noise.\n\
    5. Fixate on the dot in the center of the circle.\n\
    6. What's new: Only when you hear a beep, it’s your turn to indicate whether you saw a vertical grating on top of the noise.\n\
    7. Press the green key for 'yes' and the red key for 'no'.\n\
    8. It’s very important that you respond as fast and as accurate as possible! You only have a limited amount of time for your response.\n\
    9. If you don’t hear a beep, it’s the other person’s turn to respond. You will both see the the same stimulus and you will also see their response on your screen.\n\n\
    Press yes to continue"

    gentext(instructions)

def geninstructionsexperiment ():
    instructions = "Now you’re ready to start the experiment. Please remember:\n\
    1. Place your index finger on the left key and your middle finger on the right key.\n\
    2. Fixate on the dot in the center of the circle.\n\
    3. When you hear a beep it’s your turn. If you don’t hear a beep, you will see your partner’s response.\n\
    4. Press the green key for 'yes' and the red key for 'no'.\n\
    5. Please respond as quickly and as accurately as possible! \n\
    6. Once you finished one block, you’ll be asked if you’re ready for the next block.\n\
    7. After every second block, you will have a break.\n\
    8. There will be a total of 12 blocks.\n\n\
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

def genbaseline (subjects):
    '''
        Generate the baseline stimulus (dynamic noise + red fixation dot)
    '''
    for s in subjects:
        s.noise.phase += (10 / 128.0, 10 / 128.0)
        s.noise.draw()
        s.reddot.draw()

def gendecisionint (subjects, condition):
    '''
        Generate the stimulus
        condition:
            signal
            noise
    '''
    if condition == 'noise':
        genbaseline(subjects)
    elif condition == 'signal':
        for s in subjects:
            s.noise.phase += (10 / 128.0, 10 / 128.0)
            s.noise.draw()
            s.signal.draw()
            s.reddot.draw()
    else:
        raise NotImplementedError

def genintertrial (subjects):
    '''
        Keep displaying the stimulus but also display the other person's response if it wasn't their own turn
    '''
    for s in subjects:
        s.noise.phase += (10 / 128.0, 10 / 128.0)
        s.noise.draw()
        s.greendot.draw()

    # if subject one/two is in an acting state and responded, add their response to the response box of subject two/one
    if stwo.state:
        if stwo.response != "noresponse":
            sone.indicatordict[stwo.response].draw()
    if sone.state:
        if sone.response != "noresponse":
            stwo.indicatordict[sone.response].draw()


def fetchbuttonpress (subjects):
    '''
        Get the button box input from the acting subject
        Return the response (yes/ no) and the reaction time
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

def updatespeakerbalance ():
    '''
        Update the volume level of the left and right speaker so that only the acting subject can hear the beep
    '''
    for s in subjects:
        if s.state:
            #run(["amixer", "-D", "pulse", "sset", "Master", s.actingheadphonebalance, "quiet"])
            pass

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
    sone_ack, stwo_ack = None, None

    while (sone_ack != 'yes') or (stwo_ack != 'yes'):
        resp1 = sone.kb.getKeys(clear=False)
        resp2 = stwo.kb.getKeys(clear=False)

        if resp1:
            for r in resp1:
                if sone_ack != 'yes': sone_ack = sone.buttons[str(r.name)]
        if resp2:
            for r in resp2:
                if stwo_ack != 'yes': stwo_ack = stwo.buttons[str(r.name)]
    sone.kb.clearEvents(eventType="keyboard")
    stwo.kb.clearEvents(eventType="keyboard")

def getexperimenterack ():
    '''
        Wait for the experimenter input
            q: quit experiment
            space: continue
    '''
    keys = expkb.waitKeys(keyList=["q", "space"], clear=True)
    if "q" in keys: # exit experiment
        window.close()
        core.quit()

def genactingstates ():
    '''
        Randomly generate list including the subject states (act/ observe)
    '''
    return np.random.choice(a=[True, False], size=ntrials)

# update speaker balance for the first time
updatespeakerbalance()

# specifications of output file
_thisDir = os.path.dirname(os.path.abspath(__file__))
expName = 'DDM'
filename = _thisDir + os.sep + u'data/%s_pair%s_%s' % (expName, expinfo['pair'], data.getDateStr())

triallist = [{"condition": "signal"}, {"condition": "noise"}] * (ntrials//2)

exphandler = data.ExperimentHandler(name=expName, extraInfo=expinfo, saveWideText=True, dataFileName=filename)
for b in blocks:
    exphandler.addLoop(data.TrialHandler(trialList=triallist, nReps=1, method='random', originPath=-1, extraInfo=expinfo) )

##### PRACTICE TRIALS #####

# diplay welcome screen
genstartscreen()
window.flip()
getacknowledgements()

# display instructions for practice trials
geninstructionspractice()
window.flip()
getacknowledgements()

# set up practice trials
npracticetrials = 2 # needs to be an even number

# make sure signal/noise and acting/observing are equally distributed for practice trials
practicestates = [False, True] * (npracticetrials//2)
practicetriallist = ['signal', 'noise'] * (npracticetrials//2)

# shuffle the lists
shuffle(practicestates)
shuffle(practicetriallist)

# make an iterator object
iterstates = iter(practicestates)

# traverse through practice trials
for idx in range(npracticetrials):
    # subject state update
    updatestate()
    # update the speaker balance to play the beep for the right subject
    updatespeakerbalance()

    # display baseline
    # wait for a random time between 2 to 4 seconds
    for frame in secondstoframes( np.random.uniform(2, 4) ):
        genbaseline(subjects)
        window.flip()

    sone.kb.clearEvents(eventType='keyboard')
    stwo.kb.clearEvents(eventType='keyboard')

    # preparing time for next window flip, to precisely co-ordinate window flip and beep
    nextflip = window.getFutureFlipTime(clock='ptb')
    beep.play(when=nextflip)

    response = [] # we have no response yet
    for frame in secondstoframes(2.5):
        gendecisionint(subjects, practicetriallist[idx])
        window.flip()

        # fetch button press
        if not response:
            response = fetchbuttonpress(subjects)
        else:
            break

    # need to explicity call stop() to go back to the beginning of the track
    # we reset after collecting a response, otherwise the beep is stopped too early
    beep.stop()

    # display inter trial interval for 2s
    for frame in secondstoframes(2):
        genintertrial(subjects)
        window.flip()


##### MAIN EXPERIMENT #####

# display instructions for experiment
geninstructionsexperiment()
window.flip()
getacknowledgements()

# variables for data saving
block=0

# start MAIN EXPERIMENT
for trials in exphandler.loops:

    # variables for data saving
    block+=1

    # make an iterator object
    iterstates = iter(genactingstates())

    # traverse through trials
    for trial in trials:

        # subject state update
        updatestate()
        # update the speaker balance to play the beep for the right subject
        updatespeakerbalance()

        # save trial data to file
        exphandler.addData('block', block)
        exphandler.addData('trial', trials.thisTrialN)
        exphandler.addData('s1_state', sone.state)

        # display baseline for a random time between 2 to 4 seconds
        for frame in secondstoframes( np.random.uniform(2, 4) ):
            genbaseline(subjects)
            window.flip()

        sone.kb.clearEvents(eventType='keyboard')
        stwo.kb.clearEvents(eventType='keyboard')

        sone.kb.clock.reset()
        stwo.kb.clock.reset()

        # preparing time for next window flip, to precisely co-ordinate window flip and beep
        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)

        response = []  # we have no response yet
        for frame in secondstoframes(2.5):
            gendecisionint(subjects, trials.thisTrial['condition'])
            window.flip()

            # fetch button press
            if not response:
                response = fetchbuttonpress(subjects)
            else:
                break

        # need to explicity call stop() to go back to the beginning of the track
        # we reset after collecting a response, otherwise the beep is stopped too early
        beep.stop()

        # display inter trial interval for 2s
        for frame in secondstoframes(2):
            genintertrial(subjects)
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
    if block % 2 == 0 and block != blocks[-1]:
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
