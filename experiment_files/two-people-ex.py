# -*- coding: utf-8 -*-
#===============
# Import modules
#===============

import os
import numpy as np
import psychtoolbox as ptb
from psychopy import visual, event, core, gui, data, sound
from psychopy.sound import Sound
from numpy.random import random

#=========
# Settings
#=========
### TODO Possibly move parameter values to a separate file
### TODO add a text box for entering participant and pair numbers
datapath = 'data'
participant1 = 'x'
participant2 = 'y'
pair_num = 1
exp_info = {'participant1': participant1, 'participant2': participant2, 'pair': pair_num}
scrsize = (1024,768)
changetime = 2.5
timelimit = 2.5
n_trials = 5
ind_threshold1 = 0.04 # between 0 and 1
ind_threshold2 = 0.03

# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = 'ddm'

# Create a unique filename for the experiment data
if not os.path.isdir(datapath):
    os.makedirs(datapath)
data_fname = str(exp_info['pair']) + '_' + exp_info['date']
data_fname = os.path.join(datapath, data_fname)

### TODO Possibly track entire experiment duration

#==========================
# Create window and stimuli
#==========================

# Open two windows
### TODO Change to fullscreen
win1 = visual.Window(size=scrsize, units='pix', fullscr=False)
win2 = visual.Window(size=scrsize, units='pix', fullscr=False)

# Define instructions
instructions_individual = "Instructions:\n\
Your task is to indicate if you see a vertical grating or not.\n\
1. At the start of each trial, a red dot is shown in the middle of the screen.\n\
2. When you hear a beep, you may press one of the buttons to indicate if you saw a vertical grating or not.\n\
3. Press the left key for 'yes' and the right key for 'no'.\n\
4. After a short break, the procedure will be repeated from step one.\n\
5. After 80 trials, you will have a break.\n\
6. After the break, press the spacebar when ready to continue.\n\
7. There will be a total of 6 blocks. \n\n\
Press spacebar when ready."

### TODO Replace with real text
instructions_dyadic = "Instructions:\n\ PLACEHOLDER"


start_message1 = visual.TextStim(win1,
                                text="Press spacebar to start.",
                                color='black', height=20)
start_message2 = visual.TextStim(win2,
                                text="Press spacebar to start.",
                                color='black', height=20)
ind_instructions1 = visual.TextStim(win1,
                                text=instructions_individual,
                                color='black', height=20)
ind_instructions2 = visual.TextStim(win2,
                                text=instructions_individual,
                                color='black', height=20)
dyadic_instructions1 = visual.TextStim(win1,
                                text=instructions_dyadic,
                                color='black', height=20)
dyadic_instructions2 = visual.TextStim(win2,
                                text=instructions_dyadic,
                                color='black', height=20)

thanks1 = visual.TextStim(win1,
                            text="Thank you for participating!",
                            color='black', height=20)
thanks2 = visual.TextStim(win2,
                            text="Thank you for participating!",
                            color='black', height=20)

# Grating stimuli, always pairs of stimuli for the two participants
X = 512; # width of the gabor patch in pixels
sf = .02; # spatial frequency, cycles per pixel
noiseTexture = random([X,X])*2.-1. # a X-by-X array of random numbers in [-1,1]

gabor_texture = (
    visual.filters.makeGrating(res=X, cycles=X * sf) *
    visual.filters.makeMask(matrixSize=X, shape='circle', range=[0, 1])
)

# signal grating patch
s1 = visual.GratingStim(
    win = win1, tex = gabor_texture, mask = "circle",
    size = X, contrast = 1.0, opacity = ind_threshold1,
)

s2 = visual.GratingStim(
    win = win2, tex = gabor_texture, mask = 'circle',
    size = X, contrast = 1.0, opacity = ind_threshold2,
)

# noise patch
n1 = visual.RadialStim(
    win = win1, mask='none', tex = noiseTexture,
    size = X, contrast = 1.0, opacity = 1.0,
)

n2 = visual.RadialStim(
    win = win2, mask='none', tex = noiseTexture,
    size = X, contrast = 1.0, opacity = 1.0,
)

fixation1 = visual.GratingStim(
            win=win1, size=5, units='pix', pos=[0,0],
            sf=0, color=[1.0, -1.0, -1.0],mask='circle'
)
fixation2 = visual.GratingStim(
            win=win2, size=5, units='pix', pos=[0,0],
            sf=0, color=[1.0, -1.0, -1.0],mask='circle'
)

pretrial1 = visual.GratingStim(  ### TODO Get rid of this later
            win=win1, size=5, units='pix', pos=[0,0],
            sf=0, color='blue',mask='circle'
)
pretrial2 = visual.GratingStim(  ### TODO Get rid of this later
            win=win2, size=5, units='pix', pos=[0,0],
            sf=0, color='blue',mask='circle'
)

intertrial1 = visual.GratingStim(
            win=win1, size=5, units='pix', pos=[0,0],
            sf=0, color='green',mask='circle'
)

intertrial2 = visual.GratingStim(
            win=win2, size=5, units='pix', pos=[0,0],
            sf=0, color='green',mask='circle'
)

grey1 = visual.GratingStim(
            win=win1, size=15, units='pix', pos=[0,0],
            sf=0, color='gray',mask='circle'
)

grey2 = visual.GratingStim(
            win=win2, size=15, units='pix', pos=[0,0],
            sf=0, color='gray',mask='circle'
)

signal_decision = visual.GratingStim(
            win=win2, size=128, units='pix', pos=[0,0],
            sf=0, color="blue",mask='circle'
)

beep = sound.Sound('A', secs=0.5)

### TODO Setup button boxes here
# P1 is keys [1,2]
# P2 is keys [7,8] (TODO double-check this in the lab)

#================================
### TODO Add practice trials here
#================================

#==========================
### TODO Add titration here
#==========================

#===============
# Trial sequence
#===============

trial_list = [
            {"condition": "signal", "correct_response": "a"},
            {"condition": "noise", "correct_response": "d"}
            ]

trials = data.TrialHandler(trial_list,nReps=n_trials, extraInfo=exp_info,
                           method='random', originPath=datapath)

#======================================
# Start the main part of the experiment
#======================================

# Show start message and instructions
start_message1.draw()
start_message2.draw()
win1.flip()
win2.flip()
keys = event.waitKeys(keyList=['space', 'escape'])
rt_clock = core.Clock() # for response times
change_clock = core.Clock() # for changing stimuli

if exp_info['pair'] % 2 == 0:
    # Start even-numbered pairs in individual condition
    ind_instructions1.draw()
    ind_instructions2.draw()
    win1.flip()
    win2.flip()

    # Go through the trials
    for trial in trials:

        change_clock.reset()
        wait_for = np.random.uniform(2,4)
        now = ptb.GetSecs()
        beep.play(when=now + wait_for)

        while change_clock.getTime() <= wait_for:

            n1.draw() # draw noise in the background
            grey1.draw()
            pretrial1.draw()
            win1.flip()

        if trial['condition']=="signal":
            n1.draw() # draw noise in the background
            s1.draw() # draw grating on top of noise
            grey1.draw()
            fixation1.draw()
            win1.flip()
        else:
            n1.draw() # draw noise in the background
            grey1.draw()
            fixation1.draw()
            win1.flip()

        # Set the RT clock to 0
        rt_clock.reset()

        # For the duration of 'changetime',
        # Listen for an 'a' or 'd' or escape press
        change_clock.reset()
        while change_clock.getTime() <= changetime:
            keys = event.getKeys(keyList=['escape','a','d'])
            if len(keys) > 0:
                break

            else:
                rt = timelimit
                timeout = 1

        # Analyze the keypress
        if keys:
            if 'escape' in keys:
                # Escape press = quit the experiment
                break
            else:
                rt = rt_clock.getTime()
                resp_key = keys
                timeout = 0

        change_clock.reset()

        # intertrial interval
        while change_clock.getTime() <= changetime:
            n1.draw() # draw noise in the background
            grey1.draw()
            intertrial1.draw()
            win1.flip()

        # Add the current trial's data to the TrialHandler
        trials.addData('rt', rt)
        trials.addData('resp_key', resp_key[0])
        trials.addData('timeout', timeout)


else:
    dyadic_instructions1.draw()
    dyadic_instructions2.draw()
    win1.flip()
    win2.flip()

    if np.random.uniform() > .5:
        # P1 is acting, keys to listen to: 1 and 2
        change_clock.reset()
        wait_for = np.random.uniform(2,4)
        now = ptb.GetSecs()
        beep.play(when = now + wait_for)

        while change_clock.getTime() <= wait_for:

            n1.draw() # draw noise in the background
            s1.draw() # draw grating on top of noise
            grey1.draw()
            fixation1.draw()

            n2.draw() # draw noise in the background
            s2.draw() # draw grating on top of noise
            grey2.draw()
            fixation2.draw()

            win1.flip()
            win2.flip()

        # Reset the RT and stimuli clock
        rt_clock.reset()
        change_clock.reset()
        while change_clock.getTime() <= changetime:
            keys = event.getKeys(keyList=['1','2'])
            if len(keys) > 0:
                break

            else:
                rt = timelimit
                timeout = 1
            # Analyze the keypress
            if keys:
                rt = rt_clock.getTime()
                resp_key = keys
                timeout = 0

            change_clock.reset()
            if keys[0] == '1':
                signal_decision.draw()
                win1.flip()
                win2.flip()
            else:
                win1.flip()
                win2.flip()

            # Intertrial interval
            while change_clock.getTime() <= changetime:
                n1.draw() # draw noise in the background
                grey1.draw()
                intertrial1.draw()
                win1.flip()

            # Add the current trial's data to the TrialHandler
            trials.addData('rt', rt)
            trials.addData('resp_key', resp_key[0])
            trials.addData('timeout', timeout)
            trials.addData('acting_participant', participant1)

    else:
        # P2 is acting, keys to listen to: 7 and 8
        change_clock.reset()
        wait_for = np.random.uniform(2,4)
        now = ptb.GetSecs()
        beep.play(when = now + wait_for)

        while change_clock.getTime() <= wait_for:
            n1.draw() # draw noise in the background
            s1.draw() # draw grating on top of noise
            grey1.draw()
            fixation1.draw()

            n2.draw() # draw noise in the background
            s2.draw() # draw grating on top of noise
            grey2.draw()
            fixation2.draw()

            win1.flip()
            win2.flip()

                # Reset the RT and stimuli clock
        rt_clock.reset()
        change_clock.reset()
        while change_clock.getTime() <= changetime:
            keys = event.getKeys(keyList=['1','2'])
            if len(keys) > 0:
                break

            else:
                rt = timelimit
                timeout = 1
            # Analyze the keypress
            if keys:
                rt = rt_clock.getTime()
                resp_key = keys
                timeout = 0

        change_clock.reset()
        if keys[0] == '1':
            signal_decision.draw()
            win1.flip()
            win2.flip()
        else:
            win1.flip()
            win2.flip()

        # Intertrial interval
        while change_clock.getTime() <= changetime:
            n1.draw() # draw noise in the background
            grey1.draw()
            intertrial1.draw()
            win1.flip()

        # Add the current trial's data to the TrialHandler
        trials.addData('rt', rt)
        trials.addData('resp_key', resp_key[0])
        trials.addData('timeout', timeout)
        trials.addData('acting_participant', participant1)

#===============
# End experiment
#===============

# Save all data to a file
trials.saveAsWideText(data_fname + '.csv', delim=',')

change_clock = core.Clock()
change_clock.reset()

while change_clock.getTime() <= 3:
    thanks1.draw()
    thanks2.draw()
    win1.flip()
    win2.flip()

# Quit the experiment
win1.close()
win2.close()
core.quit()
