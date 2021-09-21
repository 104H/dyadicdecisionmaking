import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual, event, core, monitors, data
from psychopy.data import QuestHandler
import stimuli

# set the number of trials
numberOfTrials = 75 # should be 100

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

# stimulus draw functions for signal and noise
def draw_signal(noise, signal, fixation):
    noise = stimulus.updateNoise()
    noise.draw()
    signal.draw()
    # create composite fixation target
    for grating in fixation:
        grating.draw()

def draw_noise(noise, fixation):
    noise = stimulus.updateNoise()
    noise.draw()
    # create composite fixation target
    for grating in fixation:
        grating.draw()


def genendscreen():
    instructions = "You have finished the titration.\n\n\
    Please wait"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='black', height=20).draw()

def geninstrtitration():
    instructions = "Please read the instructions carefully.\n\
    1. Now we will determine your individual threshold for recognizing the vertical grating.\n\
    2. The procedure is the same as before: Press the green key if you saw a grating, and the red key if you didn’t.\n\
    3. Fixate on the red dot in the center of the circle.\n\
    4. The visibility of the grating will be adjusted throughout the trials.\n\n\
    Press yes to continue"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='black', height=20).draw()

def geninstrfamiliarization():
    instructions = "Please read the instructions carefully.\n\
    1. Place your index finger on the left key and your middle finger on the right key.\n\
    2. First, you will become familiar with the stimulus and the handling of the button box.\n\
    3. For the stimulus, a red dot is shown in the middle of the screen, surrounded by a circular pattern that looks similar to white noise.\n\
    4. You need to indicate whether you saw a vertical grating on top of the noise.\n\
    5. Fixate on the dot in the center of the circular pattern.\n\
    6. Press the green key for 'yes' and the red key for 'no'.\n\n\
    Press yes to continue"

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
    keys = ["1", "2"] if chamber == "1" else ["7", "8"] # first one is first interval

    # the screen
    window = psychopy.visual.Window(size=(M_WIDTH, M_HEIGHT), units='pix', screen=int(chamber), fullscr=False, pos=None, blendMode='add', useFBO=True, monitor=myMon)
    window.mouseVisible = False

    # the stimulus
    stimulus = stimuli.stim(window=window, xoffset=0, threshold=initial_threshold)
    signal = stimulus.signal
    noise = stimulus.noise
    fixation = stimulus.fixation_red

    decision_interval = "Press the green button if you saw stripes in the first interval, or the red button if you saw stripes in the second interval."

    decision = visual.TextStim(window,
                    text=decision_interval, pos=(0,0),
                    color='black', height=20)


    '''
    1. Familiarization
    '''
    key = []
    signal.opacity = initial_threshold # set contrast to

    # randomly pick which interval has signal
    signal_int = np.random.randint(2)

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
    for frame in secondstoframes(5):
        decision.draw()
        window.flip()

        # get button press
        if not key:
            key = event.getKeys(keys)
        else:
            break

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
    key = event.waitKeys(keyList=keys[:1])
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
        for frame in secondstoframes(5):
            decision.draw()
            window.flip()

            # get button press
            if not key:
                key = event.getKeys(keys)
            else:
                break

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
