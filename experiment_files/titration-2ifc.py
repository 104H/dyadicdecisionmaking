import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual, event, core, monitors, data, prefs
from psychopy.data import QuestHandler
import stimuli


# set up sound for beeps
prefs.hardware['audioLib'] = ['PTB']

from psychopy import sound
sound.setDevice('USB Audio Device: - (hw:3,0)')

from psychopy.sound import Sound
beep = Sound('A', secs=0.5, volume=0.1)

# set the number of trials
numberOfTrials = 75

# Directory Specs
HOME = os.getcwd()
DATA = '/data/'

# Subject data dictionary
subjectData = {'pair_id': [], 'titration_counter': [], 'chamber':[], 'threshold': [], 'threshold_list': [], 'contrast_list': [], 'method': "2AFC" }

# Method to use ("staircase" or "quest")
method = "quest"

# monitoring the while loop with..
titration_over = False

# monitoring how often the titration has been done
titration_counter = 0

# initial threshold
initial_threshold = 0.02
# prior std for quest
prior_std = 0.01

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH
M_HEIGHT = stimuli.M_HEIGHT
REFRESH_RATE = stimuli.REFRESH_RATE

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=80)
myMon.setSizePix([M_WIDTH, M_HEIGHT])

# get pair id via command-line argument
try:
    pair_id = int(sys.argv[1])
except:
    print('Please enter a number as pair id as command-line argument!')
    pair_id = input()

subjectData['pair_id'] = pair_id

def secondstoframes (seconds):
    return range( int( np.rint(seconds * REFRESH_RATE) ) )

# draws a composite fixation point
def draw_fixation(fixation):

    for grating in fixation:
        grating.draw()

# stimulus draw functions for signal and noise
def draw_signal(noise, signal, fixation):
    noise = stimulus.updateNoise()
    noise.draw()
    signal.draw()
    # create composite fixation target
    draw_fixation(fixation)

def draw_noise(noise, fixation):
    noise = stimulus.updateNoise()
    noise.draw()
    # create composite fixation target
    draw_fixation(fixation)



def geninstrfamiliarization():
    instructions = "Please read the instructions carefully.\n\
    1. Place your index finger on the left button and your middle finger on the right button.\n\
    2. Fixate on the red dot in the center of the screen. \n\
    3. You will see two intervals of 750ms each. Both of them will show noise and in one there will be stripes on top of the noise.\n\
    4. Please indicate which interval had the stripes:\n\
    When you hear the beep, press the red button for the first interval and the green button for the second interval.\n\n\
    Press the green button to continue"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='black', height=20).draw()


def geninstrtitration():
    instructions = "Please read the instructions carefully.\n\n\
    In this part of the experiment you still have to decide which interval had the stripes. \n\
    Press the red button if the stripes were in the first interval and the green button if there were stripes in the second interval. \n\
    Try to be as accurate as possible. \n\
    Sometimes the stripes will be very pale - please still try to make a decision. \n\n\
    Press the green button to start the experiment."

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='black', height=20).draw()

def genendscreen():
    instructions = "You have finished the titration.\n\n\
    Please wait"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='black', height=20).draw()

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
    keys = ["1", "2"] if chamber == "1" else ["8", "7"] # first one is first interval

    # the screen
    window = psychopy.visual.Window(size=(M_WIDTH, M_HEIGHT), units='pix', screen=int(chamber), fullscr=True, pos=None, blendMode='add', useFBO=True, monitor=myMon)
    window.mouseVisible = False

    # the stimulus
    stimulus = stimuli.stim(window=window, xoffset=0, threshold=initial_threshold)
    signal = stimulus.signal
    noise = stimulus.noise
    fixation = stimulus.fixation_red

    #make black fixation
    fixation_black = stimulus.fixation_black

    decision_interval = "Press the red button if you saw stripes in the first interval, or the green button if you saw stripes in the second interval."

    decision = visual.TextStim(window,
                    text=decision_interval, pos=(0,0),
                    color='black', height=20)

    '''
    1. Familiarization
    '''
    geninstrfamiliarization()
    window.flip()
    key = event.waitKeys(keyList=keys[1])
    window.flip()

    for _ in range(10):
        key = []
        contrast = np.random.normal(loc=initial_threshold,scale=prior_std)
        signal.opacity = contrast # set contrast to

        # randomly pick which interval has signal
        signal_int = np.random.randint(2)

        # Fixation period
        for frame in secondstoframes(2.5):
            draw_fixation(fixation_black)
            window.flip()

        if not signal_int: # signal in first interval
            # show interval 1 for 750 ms
            for frame in secondstoframes(0.75):
                draw_signal(noise, signal, fixation) # draw signal
                window.flip()

            # cool down of 500 ms
            for frame in secondstoframes(0.5):
                window.flip()

            # show interval 2 for 750 ms
            for frame in secondstoframes(0.75):
                draw_noise(noise, fixation) # draw noise
                window.flip()
        else: # signal in second interval
            # show interval 1 for 750 ms
            for frame in secondstoframes(0.75):
                draw_noise(noise, fixation) # draw noise
                window.flip()

            # cool down of 500 ms
            for frame in secondstoframes(0.5):
                window.flip()

            # show interval 1 for 750 ms
            for frame in secondstoframes(0.75):
                draw_signal(noise, signal, fixation) # draw signal
                window.flip()

        event.clearEvents()
        # decision interval of 2.5 s

        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)

        for frame in secondstoframes(5):
            decision.draw()
            window.flip()

            # get button press
            if not key:
                key = event.getKeys(keys)
            else:
                break
        beep.stop()
        window.flip()
        core.wait(3) # wait for 3 s before next trial

    '''
    2. Titration
    '''

    #the ladder

    if method=="quest":
        staircase = QuestHandler(
                                    startVal=initial_threshold,
                                    startValSd=prior_std,
                                    pThreshold=0.82, # gives 75 % for 2IFC
                                    gamma=0.5,
                                    delta=0.05,
                                    #stopInterval=0,
                                    nTrials=numberOfTrials,
                                    minVal=0.005,
                                    maxVal=0.1,
                                    method='quantile'
                                    )
    elif method=="staircase":
        staircase = data.StairHandler(startVal = initial_threshold, nReversals=10,
                          stepType = 'log', stepSizes=[0.08,0.04,0.04,0.02],
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=numberOfTrials, minVal=0, maxVal=1)

    geninstrtitration() # display instructions
    window.flip()
    key = event.waitKeys(keyList=keys[1])
    window.flip()

    """
    Main section:
        1. use the ladder already created to change the contrast of the grating
        2. Show two intervals to subject
        3. During the decision interval, collect response
        4. Pass on response evaluation to ladder (0 if subject responded correctly, 1 if subject did not)
        5. Do 1 to 4 for ntimes set in ladder constructor
    """
    # list that is filled with the staircase values
    staircase_medians = []
    staircase_contrasts = []

    for contrast in staircase:
        key = []
        signal.opacity = contrast # set contrast to the next value from the staircase

        # randomly pick which interval has signal
        signal_int = np.random.randint(2)

        # Fixation period
        for frame in secondstoframes(2.5):
            draw_fixation(fixation_black)
            window.flip()

        if not signal_int: # signal in first interval
            # show interval 1 for 750 ms
            for frame in secondstoframes(0.75):
                draw_signal(noise, signal, fixation) # draw signal
                window.flip()

            # cool down of 500 ms
            for frame in secondstoframes(0.5):
                window.flip()

            # show interval 2 for 750 ms
            for frame in secondstoframes(0.75):
                draw_noise(noise, fixation) # draw noise
                window.flip()
        else: # signal in second interval
            # show interval 1 for 750 ms
            for frame in secondstoframes(0.75):
                draw_noise(noise, fixation) # draw noise
                window.flip()

            # cool down of 500 ms
            for frame in secondstoframes(0.5):
                window.flip()

            # show interval 1 for 750 ms
            for frame in secondstoframes(0.75):
                draw_signal(noise, signal, fixation) # draw signal
                window.flip()

        event.clearEvents()
        nextflip = window.getFutureFlipTime(clock='ptb')
        beep.play(when=nextflip)
        # decision interval of 2.5 s
        for frame in secondstoframes(5):
            decision.draw()
            window.flip()

            # get button press
            if not key:
                key = event.getKeys(keys)
            else:
                break
        beep.stop()
        if keys[signal_int] in key: # check if decision is correct
            response = 1
            print(response)
        else:
            response = 0
            print(response)
        window.flip()
        staircase.addResponse(response)
        core.wait(3) # wait for 3 s before next trial

        staircase_contrasts.append(contrast)
        if method == "quest":
            staircase_medians.append(staircase.quantile(0.5))

    if method == "quest":
        #fill subject dictionary with threshold and staircase value list
        subjectData["threshold"] = staircase.mean()
        subjectData['threshold_median'] = staircase.quantile(0.5)
        subjectData['threshold_mean'] = staircase.mean()
        subjectData['threshold_list'] = staircase_medians
        subjectData['contrast_list'] = staircase_contrasts



        print('The titration values are: ')
        for value in staircase_medians:
            print("%.4f" % value)
        print("The subject's mean threshold is: " + str(staircase.mean())+ "\n")
        print("The subject's median threshold is: " + str(staircase.quantile(0.5)))
        print("The subject's mode threshold is: " + str(staircase.mode()))

    elif method == "staircase":
        approxThreshold = np.average(staircase.reversalIntensities[-6:])
        subjectData['threshold'] = approxThreshold
        print('mean of final 6 reversals = %.3f' % (approxThreshold))

    genendscreen()
    window.flip()
    core.wait(5)
    window.close()

    print('Titration result sufficient? Enter y/n')
    answer = input()

    # if the titration is sufficient the script stops, if not it repeats and increases the titration counter
    if answer !='y' and answer !='n':
        print("Enter yes(y) or no(n) !")
        answer = input()
    else:
        if answer == 'y':
            titration_over = True
            # Create directory and save as JSON
            DATAPATH = HOME+DATA+str(pair_id)
            if not os.path.exists(DATAPATH):
                os.makedirs(DATAPATH)
            os.chdir(DATAPATH)
            with open('data_chamber'+chamber+'.json', 'w') as fp:
                json.dump(subjectData, fp)
        elif answer == 'n':
            Titration_over = False
