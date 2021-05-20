import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual
from psychopy.data import QuestHandler
from psychopy import core
from stimuli import stimulus as stim


"""
Set-up section:
    1. Create the screen
    2. Create the instructions message to be shown on intial screen
    3. Create the stimulus. This needs to be replcaed with the stimulus being used in the experiment
    4. Create the ladder object for controlling stimulus and measuring threshold. The ladder has to be updated to match the experiment needs.
"""


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

# Gabor patch global variables
CYCLES = 10 # required cycles for the whole patch
X = 256; # size of texture in pixels, needs to be to the power of 2!
sf = CYCLES/X; # spatial frequency for texture, cycles per pixel
gabortexture = (
    visual.filters.makeGrating(res=X, cycles=X * sf) *
    visual.filters.makeMask(matrixSize=X, shape="circle", range=[0, 1])
)


# get pair id via command-line argument
try:
    pair_id = int(sys.argv[1])
except:
    print('Please enter a number as pair id as command-line argument!')
    pair_id = input()
    
subjectData['pair_id'] = pair_id

while titration_over == False:
    titration_counter += 1
    subjectData['titration_counter'] = titration_counter
    
    # input the chamber number in which titration takes place
    chamber = []
    if chamber == []:
        print("Enter chamber number (1 or 2):")
        chamber = input()
    elif chamber != 1 & chamber != 2:
        print("Wrong! Enter chamber number (1 or 2):")
        chamber = input()
    else: 
        print("You already entered a chamber number! You entered:" + chamber)
        
    subjectData['chamber'] = chamber

    """
    Opening section:
        1. Show subject instructions and give option to not continue
    """
        
    # screen
    window = psychopy.visual.Window(size=(1920, 1080), units='pix', screen=int(chamber), fullscr = False, pos = None) 
    m = psychopy.event.Mouse(win=window)
    m.setVisible(0)

    # message for initial screen
    message1 = visual.TextStim(window, pos=(0,0),
                                text="Instruction:\n"
                                    "Press Right when you see vertical lines, Left when you don't\n \n"
                                    "Hit a key when ready.\n\n"
                                    "Press ESC to escape" ) 

    # the old test stimulus
#    stimulus = visual.GratingStim(
#                                SCREEN,
#                                opacity=1,
#                                contrast=1
#                                ,mask='circle',
#                                tex="sin",
#                                units='pix',
#                                color=[1,1,1],
#                                size=800,
#                                sf=0.02, 
#                                ori=0
#                                )   

# the actual stimulus
    stimuli = stim(X=X, window=window, xoffset=0, gabortexture=gabortexture, threshold=threshold)
    stimulus = stimuli.signal
                                
    #the ladder
    staircase = QuestHandler(
                                startVal=0.5,
                                startValSd=0.2,
                                pThreshold=0.75, #was 0.63 
                                gamma=0.01,
                                nTrials=10,
                                minVal=0,
                                maxVal=1
                                )   
     
    while True:
        message1.draw()
        window.flip()
        key = psychopy.event.getKeys()
        if len(key) > 0:
            if 'escape' in key:
                window.close()
                core.quit()
            else:
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
        stimulus.opacity = contrast #update the difficulty or contrast from the staircase
        while not key:
            stimulus.draw() #draw the stimulus
            window.flip()
            key = psychopy.event.getKeys(keyList=['left','right'])
        if 'left' in key:
            response = 0
            staircase_means.append(staircase.mean())
        else:
            response = 1
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
    print(staircase_means)

    window.flip()
    #core.wait(2)
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
            DATAPATH = HOME+DATA+pair_id
            if not os.path.exists(DATAPATH):
                os.makedirs(DATAPATH)
            os.chdir(DATAPATH)
            with open('data_chamber'+chamber+'.json', 'w') as fp:
                json.dump(subjectData, fp)
        elif answer == 'n':
            Titration_over = False

