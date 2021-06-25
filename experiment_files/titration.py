import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual
from psychopy.data import QuestHandler
from psychopy.hardware import keyboard
from psychopy import core
import stimuli


#import pdb; pdb.set_trace()

"""
Set-up section:
    1. Create the screen
    2. Create the instructions message to be shown on intial screen
    3. Create the stimulus. This needs to be replcaed with the stimulus being used in the experiment
    4. Create the ladder object for controlling stimulus and measuring threshold. The ladder has to be updated to match the experiment needs.
"""

# set the number of trials (for testing)!
numberOfTrials = 100 # should be 100

kb = keyboard.Keyboard()

# Directory Specs
HOME = os.getcwd()
DATA = '/data/'
# Subject data dictionary
subjectData = {'pair_id': [], 'titration_counter': [], 'chamber':[], 'threshold': [], 'threshold_list': [] }
# monitoring the while loop with..
titration_over = False
# monitoring how often the titration has been done
titration_counter = 0
# initial threshold
threshold = 1
# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH
M_HEIGHT = stimuli.M_HEIGHT

# get pair id via command-line argument
try:
    pair_id = int(sys.argv[1])
except:
    print('Please enter a number as pair id as command-line argument!')
    pair_id = input()

subjectData['pair_id'] = pair_id

# stimulus draw function
def draw_stim(noise, signal, reddot):
    noise.phase += (10 / 128.0, 10 / 128.0)
    noise.draw()
    signal.draw()
    reddot.draw()

def genendscreen():
    instructions = "You have finished the titration.\n\n\
    Please wait"

    visual.TextStim(window,
                    text=instructions, pos=(0, 0),
                    color='black', height=20).draw()

def geninstrtitration():
    instructions = "Please read the instructions carefully.\n\
    1. Now we will determine your individual threshold for recognizing the vertical grating.\n\
    2. The procedure is the same as before: when you hear a beep, press the green key if you saw a grating, and the red key if you didn’t.\n\
    3. Fixate on the dot in the center of the circle.\n\
    3. The visibility of the grating will be adjusted throughout the trials.\n\n\
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
    elif chamber != "1" & chamber != "2":
        print("Wrong. Enter chamber number (1 or 2):")
        continue
    else:
        print("You already entered a chamber number! You entered:" + chamber)

    titration_counter += 1
    subjectData['titration_counter'] = titration_counter
    subjectData['chamber'] = chamber

    # variables for button box input
    keys = ["2", "1"] if chamber == "1" else ["7", "8"] # first one is yes

    # the screen
    window = psychopy.visual.Window(size=(M_WIDTH, M_HEIGHT), units='pix', screen=int(chamber), fullscr=False, pos=None, blendMode='add', useFBO=True)
    window.mouseVisible = False # hide cursor

    # the stimulus
    stimulus = stimuli.stim(window=window, xoffset=0, threshold=threshold)
    signal = stimulus.signal
    noise = stimulus.noise
    reddot = stimulus.reddot

    '''
    1. Familiarization
    '''
    while True:
        geninstrfamiliarization() # display instructions
        window.flip()
        key = kb.getKeys()
        if len(key) > 0:
            if keys[0] in key:
                break

    nfamtrials = 3
    famcontrast = [0.15,0.002,0.08]

    for contr in famcontrast:
        key = []
        signal.opacity = contr
        while not key:
            draw_stim(noise, signal, reddot) # draw the stimulus
            window.flip()
            key = kb.getKeys(keyList=keys)

    '''
    2. Titration
    '''

    #the ladder
    staircase = QuestHandler(
                                startVal=0.01,
                                startValSd=0.0095,
                                pThreshold=0.63,  #because it is a one up one down staircase
                                gamma=0.01,
                                nTrials=numberOfTrials,
                                minVal=0.00005,
                                maxVal=0.1
                                )

    while True:
        geninstrtitration() # display instructions
        window.flip()
        key = kb.getKeys()
        if len(key) > 0:
            if keys[0] in key:
                break


    """
    Main section:
        1. use the ladder already created to change the contrast of the grating
        2. Show the patch to subject
        3. Collect response-left is subject can see the grating, right otherwise
        4. Pass on reponse evaluation to ladder (0 if subject responded correctly, 1 if subject did not)
        5. Do 1 to 4 for ntimes set in ladder constructor
    """
    # list that is filled with the staircase values
    staircase_means = []

    for contrast in staircase:
        key = []
        signal.opacity = contrast #update the difficulty or contrast from the staircase
        while not key:
            draw_stim(noise, signal, reddot) # draw the stimulus
            window.flip()
            key = kb.getKeys(keyList=keys)
        if keys[1] in key: # if they didn't see it
            print("no")
            response = 0
            staircase_means.append(staircase.mean())
        else:
            response = 1
            print("yes")
            staircase_means.append(staircase.mean())
        staircase.addResponse(response)


    """
    End section:
        1. Show the threshold to subject.
        This part will be changed for the experiment.
        We will store the threshold in a variable for the next core block to use.
    """

    # fill subject dictionary with threshold and staircase value list
    subjectData['threshold'] = staircase.mean()
    subjectData['threshold_list'] = staircase_means

    # currently printing the threshold to the subject
    #result = 'The threshold is %0.4f' %(staircase.mean())
    #message2 = visual.TextStim(SCREEN, pos=(0,0), text=result)
    #message2.draw()

    print('The subjects threshold is: ' + str(staircase.mean()))
    print('The titration values are: ')
    for member in staircase_means:
        print("%.4f" % member)

    window.flip()
    genendscreen()
    window.flip()
    core.wait(5)
    window.close()

    answer = []
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
