import sys
import os
import time
import numpy as np
import psychopy
from psychopy import visual
from psychopy.data import QuestHandler
from psychopy import core


"""
Set-up section:
    1. Create the screen
    2. Create the instructions message to be shown on intial screen
    3. Create the stimulus. This needs to be replcaed with the stimulus being used in the experiment
    4. Create the ladder object for controlling stimulus and measuring threshold. The ladder has to be updated to match the experiment needs.
"""
# screen
SCREEN = psychopy.visual.Window(size=(1200, 1000), fullscr = False, pos = None) 
m = psychopy.event.Mouse(win=SCREEN)
m.setVisible(0)

# message for initial screen
message1 = visual.TextStim(SCREEN, pos=(0,0),
                           text="Instruction:\n"
                                "Press Right when you see vertical lines, Left when you don't\n \n"
                                "Hit a key when ready.\n\n"
                                "Press ESC to escape" ) 

# the stimulus
stimulus = visual.GratingStim(
                            SCREEN,
                            opacity=1,
                            contrast=1
                            ,mask='circle',
                            tex="sin",
                            units='pix',
                            color=[1,1,1],
                            size=800,
                            sf=0.02, 
                            ori=0
                            )   
#the ladder
staircase = QuestHandler(
                            startVal=0.5,
                            startValSd=0.2,
                            pThreshold=0.63,
                            gamma=0.01,
                            nTrials=15,
                            minVal=0,
                            maxVal=1
                            )   

def calculate_threshold():
"""
Opening section:
    1. Show subject instructions and give option to not continue
    """
    while True:
        message1.draw()
        SCREEN.flip()
        key = psychopy.event.getKeys()
        if len(key) > 0:
            if 'escape' in key:
                SCREEN.close()
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
    for contrast in staircase:
        key = []
        stimulus.opacity = contrast #update the difficulty or contrast from the staircase
        while not key:
            stimulus.draw() #draw the stimulus
            SCREEN.flip()
            key = psychopy.event.getKeys(keyList=['left','right'])
        if 'left' in key:
            response = 0
        else:
            response = 1
        staircase.addResponse(response)

    """
    End section:
        1. Show the threshold to subject. 
        This part will be changed for the experiment. 
        We will store the threshold in a variable for the next core block to use. 
    """
    threshold = staircase.mean()
    result = 'The threshold is %0.4f' %(staircase.mean())
    message2 = visual.TextStim(SCREEN, pos=(0,0), text=result)
    message2.draw()
    SCREEN.flip()
    core.wait(2)
    SCREEN.close()
    
    # Returning threshold
    return threshold