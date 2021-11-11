import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual, event, core, prefs, sound
from psychopy.sound import Sound
from psychopy.data import StairHandler
from psychopy.data import QuestHandler
from stimuli_random_dots import createDots
import stimuli_random_dots as stimuli


# set up sound for beeps
prefs.hardware['audioLib'] = ['PTB']
# sound.setDevice('USB Audio Device: - (hw:3,0)') #(not working on my computer for some reason, works in the lab though)

# set the number of trials (for testing)!
numberOfTrials = 80 # should be 100

# Directory Specs
HOME = os.getcwd()
DATA = '/data/'

# Subject data dictionary
subjectData = {'pair_id': [], 'titration_counter': [], 'chamber':[], 'threshold': [], 'threshold_list': [] }

# monitoring the while loop with.
titration_over = False

# monitoring how often the titration has been done
titration_counter = 0

threshold = .9

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH
M_HEIGHT = stimuli.M_HEIGHT
N = stimuli.N
ndots = stimuli.ndots
dotlife = stimuli.dotlife
speed = stimuli.speed

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
    instructions = "You have finished the titration.\n\n\
    Please wait"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='white', height=20).draw()
# TODO:
def instruction_titration():
    instructions = "Please read the instructions carefully.\n\
    Press yes to continue"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='white', height=20).draw()

# TODO:
def instruction_familiarization():
    instructions = "Please read the instructions carefully.\n\
    Press yes to continue"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='white', height=20).draw()


###########################
##### TITRATION START #####
###########################

while titration_over == False:
    # input the chamber number in which titration takes place

    chamber = []
    if chamber == []:
        print("Enter chamber number (1 or 2):")
        chamber = input()

        if chamber not in ["1", "2"]:
            print("Wrong. Enter chamber number (1 or 2):")
            continue
    # beep depends on the chamber number
    if chamber == "1":
        beep = Sound('A', secs=0.5, volume=0.1)
    else:
        beep = Sound('E', secs=0.5, volume=0.1)

    titration_counter += 1
    subjectData['titration_counter'] = titration_counter
    subjectData['chamber'] = chamber

    # variables for button box input
    keys = ["2", "1"] if chamber == "1" else ["7", "8"] # first one is yes

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
    # 1. Familiarization (TODO)
    # '''
    #
    # instruction_familiarization() # display instructions
    # window.flip()
    # key = event.waitKeys(keyList=keys[:1])
    #
    # famcoherence = [0.5, 0.1, 0.8, 0.5, 0.1]
    #
    # # TODO: refactor? - this code is also used for the staircase procedure
    #
    # for coh in famcoherence:
    #     direction = np.random.choice(np.array([0, 180]))
    #     movingDotPatch = createDotPatch(window, xoffset, direction, coh)
    #     key = []
    #
    #     for frame in secondstoframes( np.random.uniform(4.3, 5.8) ):
    #         pretrial_interval(greencross, stationaryDotPatch)
    #         window.flip()
    #
    #     # play beep because next is decision interval (beep should depend on chamber number)
    #
    #     event.clearEvents()
    #     nextflip = window.getFutureFlipTime(clock='ptb')
    #     beep.play(when=nextflip)
    #
    #     # decision interval: light blue cross & moving dots
    #     response = None  # we have no response yet
    #     for frame in secondstoframes(7.5):
    #         if frame % 3 == 0:
    #             decision_interval(movingDotPatch[0])
    #         elif frame % 3 == 1:
    #             decision_interval(movingDotPatch[1])
    #         elif frame % 3 == 2:
    #             decision_interval(movingDotPatch[2])
    #         else:
    #             print('error in secondstoframes decision_interval')
    #         window.flip()
    #
    #         # fetch button press: response 0 is right, response 1 is left
    #         if response is None:
    #             #event.clearEvents()
    #             key = event.getKeys(keyList=keys)
    #             if keys[1] in key:
    #                 print("left")
    #                 response = 0
    #
    #             elif keys[0] in key:
    #                 print("right")
    #                 response = 1
    #         else:
    #             if direction == 180:
    #                 print("true left")
    #                 direction_left = 0
    #             else:
    #                 print("true right")
    #                 direction_left = 1
    #             # check whether response and direction are matching and add to staircase
    #             if not (response or direction_left) or (response and direction_left):
    #                 correct = 1
    #             else:
    #                 correct = 0
    #
    #             # end decision interval
    #             break
    #
    #     beep.stop()
    #
    #     # randomly pick a stationary dot patch
    #     stationaryDotPatch = stationaryDotsList[np.random.randint(0, N)]
    #
    #     # start feedback interval
    #     if response == 0: # left
    #         draw_fixation(yellowcross)
    #         drawDots(stationaryDotPatch)
    #         window.flip()
    #         core.wait(0.75)
    #     elif response == 1: #right
    #         draw_fixation(bluecross)
    #         drawDots(stationaryDotPatch)
    #         window.flip()
    #         core.wait(0.75)


    '''
    2. Titration
    '''

    staircase = QuestHandler(
                                    startVal=0.5,
                                    startValSd=0.5,
                                    pThreshold=0.82, # gives 75 % for 2IFC
                                    gamma=0.5,
                                    delta=0.01,
                                    #stopInterval=0,
                                    nTrials=numberOfTrials,
                                    minVal=0.035,
                                    maxVal=0.8,
                                    method='quantile'
                                    )

    instruction_titration() # display instructions
    window.flip()
    key = event.waitKeys(keyList=keys[:1])
    staircase_medians = []

    for coherence in staircase:

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
                staircase.addResponse(correct)
                staircase_medians.append(staircase.quantile(0.5))

                #event.clearEvents()

                # end decision interval
                break

        beep.stop()

        # randomly pick a stationary dot patch
        stationaryDotPatch = stationaryDotsList[np.random.randint(0, N)]

        # start feedback interval
        if response == 1: # left
            drawDots(stationaryDotPatch)
            draw_fixation(yellowcross)
            window.flip()
            core.wait(0.75)
        elif response == 0: #right
            drawDots(stationaryDotPatch)
            draw_fixation(bluecross)
            window.flip()
            core.wait(0.75)

    subjectData['threshold'] = staircase.mean()
    subjectData['threshold_list'] = staircase_medians # all coherence values the participant saw during titration

    # print('reversals:')
    # print(staircase.reversalIntensities)
    # print("The subject's threshold is: = %.5f" % np.average(staircase.reversalIntensities[-6:])) # TODO: needs to be changed to match the quest method

    print(f"threshold is {staircase.mean()}")

    endscreen()
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
            DATAPATH = HOME+DATA+str(pair_id)
            if not os.path.exists(DATAPATH):
                os.makedirs(DATAPATH)
            os.chdir(DATAPATH)
            with open('data_chamber'+chamber+'.json', 'w') as fp:
                json.dump(subjectData, fp)
        elif answer == 'n':
            Titration_over = False

#########################
##### TITRATION END #####
#########################
