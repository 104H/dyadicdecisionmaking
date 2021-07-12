import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual, event, core
import questplus as qp
import stimuli


# set the number of trials (for testing)!
numberOfTrials = 150 # should be 100

# Stimuli
opacities = np.arange(start=0.001, stop=0.003, step=0.0001)
stim_domain = dict(intensity=opacities)

# Parameters of the staircase

thresholds = opacities.copy()
slopes = np.linspace(0.5, 15, 5)
lower_asymptotes = np.linspace(0.01, 0.5, 5)
lapse_rate = 0.01

param_domain = dict(threshold=thresholds,
                    slope=slopes,
                    lower_asymptote=lower_asymptotes,
                    lapse_rate=lapse_rate)

# Outcome (response)
responses = ['Yes', 'No']
outcome_domain = dict(response=responses)

# Other parameters
func = 'weibull'
stim_scale = 'log10'
stim_selection_method = 'min_entropy'
stim_selection_options = {'max_consecutive_reps': 2}
param_estimation_method = 'mean'

# Directory Specs
HOME = os.getcwd()
DATA = '/data/'

# Subject data dictionary
subjectData = {'pair_id': [], 'titration_counter': [], 'chamber':[], 'threshold': [], 'threshold_list': [], 'responses': [], 'slope': [], 'lower_asymptote': [], 'lapse_rate': [], 'method': 'questplus' }

# monitoring the while loop with..
titration_over = False

# monitoring how often the titration has been done
titration_counter = 0

# initial threshold
threshold = 0.01

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
    stimulus.updateNoise()
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
    keys = ["2", "1"] if chamber == "1" else ["7", "8"] # first one is yes

    # the screen
    window = psychopy.visual.Window(size=(M_WIDTH, M_HEIGHT), units='pix', screen=int(chamber), fullscr=False, pos=None, blendMode='add', useFBO=True)
    window.mouseVisible = False # hide cursor

    # the stimulus
    stimulus = stimuli.stim(window=window, xoffset=0, threshold=threshold)
    signal = stimulus.signal
    noise = stimulus.noise
    reddot = stimulus.reddot

    # '''
    # 1. Familiarization
    # '''
    # geninstrfamiliarization() # display instructions
    # window.flip()
    # key = event.waitKeys(keyList=keys[:1])
    #
    # famcontrast = [0.15,0.002,0.08]
    # nfamtrials = len(famcontrast)
    #
    # for contr in famcontrast:
    #     key = []
    #     signal.opacity = contr
    #     while not key:
    #         draw_stim(noise, signal, reddot) # draw the stimulus
    #         window.flip()
    #         key = event.getKeys(keyList=keys)

    '''
    2. Titration
    '''

    thresholds = []
    responses = []

    #the ladder
    staircase = qp.QuestPlus(stim_domain=stim_domain,
                 func=func,
                 stim_scale=stim_scale,
                 param_domain=param_domain,
                 outcome_domain=outcome_domain,
                 stim_selection_method=stim_selection_method,
                 stim_selection_options=stim_selection_options,
                 param_estimation_method=param_estimation_method)


    geninstrtitration() # display instructions
    window.flip()
    key = event.waitKeys(keyList=keys[:1])

    """
    Main section:
        1. use the ladder already created to change the contrast of the grating
        2. Show the patch to subject
        3. Gather responses
        4. Pass on reponse evaluation to ladder (0 if subject responded correctly, 1 if subject did not)
        5. Do 1 to 4 for ntimes set in ladder constructor
    """
    for i in range(numberOfTrials):
        key = []
        next_stim = staircase.next_stim
        signal.opacity = next_stim['intensity'] # set stimulus opacity to the next value from the staircase
        thresholds.append(next_stim['intensity'])
        while not key:
            draw_stim(noise, signal, reddot) # draw the stimulus
            window.flip()
            key = event.getKeys(keyList=keys)
        if keys[1] in key: # if the participant didn't detect signal, record a 'no' response
            print("no")
            outcome = dict(response='No')
        else:
            print("yes")
            outcome = dict(response='Yes')
        responses.append(outcome['response'])
        staircase.update(stim=next_stim, outcome=outcome)


    for param_name, value in staircase.param_estimate.items():
        print(f'    {param_name}: {value:.3f}')

    subjectData['threshold'] = staircase.param_estimate['threshold']
    subjectData['slope'] = staircase.param_estimate['slope']
    subjectData['lower_asymptote'] = staircase.param_estimate['lower_asymptote']
    subjectData['lapse_rate'] = staircase.param_estimate['lapse_rate']
    subjectData['threshold_list'] = thresholds
    subjectData['responses'] = responses

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
            DATAPATH = HOME+DATA+str(pair_id)
            if not os.path.exists(DATAPATH):
                os.makedirs(DATAPATH)
            os.chdir(DATAPATH)
            with open('data_chamber'+chamber+'.json', 'w') as fp:
                json.dump(subjectData, fp)
        elif answer == 'n':
            Titration_over = False
