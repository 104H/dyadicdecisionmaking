# Test experiment with a single person

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
datapath = 'data'
exp_info = {'participant': 'x', 'pair': 1}
scrsize = (1024,768)
changetime = 2.5
timelimit = 2.5
n_trials = 5
ind_threshold = 0.3 # between 0 and 1


# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = 'ddm'

# Create a unique filename for the experiment data
if not os.path.isdir(datapath):
    os.makedirs(datapath)
data_fname = exp_info['participant'] + '_' + exp_info['date']
data_fname = os.path.join(datapath, data_fname)


#==========================
# Create window and stimuli
#==========================

# Open a window
# (Change to fullscreen)
win = visual.Window(size=scrsize, units='pix', fullscr=False)

# Define instructions
instructions = "Instructions:\n\
Your task is to indicate if you see a vertical grating or not.\n\
1. At the start of each trial, a red dot is shown in the middle of the screen.\n\
2. When you hear a beep, you may press one of the buttons to indicate if you saw a vertical grating or not.\n\
3. Press the left key for 'yes' and the right key for 'no'.\n\
4. After a short break, the procedure will be repeated from step 1.\n\
5. After 80 trials, you will have a break.\n\
6. After the break, press the spacebar when ready to continue.\n\
7. There will be a total of 6 blocks. \n\n\
Press spacebar when ready."

start_message = visual.TextStim(win,
                                text="Press spacebar to start.",
                                color='black', height=20)
instructions = visual.TextStim(win,
                                text=instructions,
                                color='black', height=20)

thanks = visual.TextStim(win,
                            text="Thank you for participating!",
                            color='black', height=20)

X = 512; # width of the gabor patch in pixels
sf = .02; # spatial frequency, cycles per pixel
noiseTexture = random([X,X])*2.-1. # a X-by-X array of random numbers in [-1,1]

gabor_texture = (
    visual.filters.makeGrating(res=X, cycles=X * sf) *
    visual.filters.makeMask(matrixSize=X, shape="circle", range=[0, 1])
)

# signal grating patch
s = visual.GratingStim(
    win = win, tex = gabor_texture, mask = 'circle',
    size = X, contrast = 1.0, opacity = ind_threshold,
)

# noise patch
n = visual.RadialStim(
    win = win, mask='none', tex = noiseTexture,
    size = X, contrast = 1.0, opacity = 1.0,
)

fixation = visual.GratingStim(
            win=win, size=5, units='pix', pos=[0,0],
            sf=0, color=[1.0, -1.0, -1.0],mask='circle'
)

pretrial = visual.GratingStim(
            win=win, size=5, units='pix', pos=[0,0],
            sf=0, color='blue',mask='circle'
)

intertrial = visual.GratingStim(
            win=win, size=5, units='pix', pos=[0,0],
            sf=0, color='green',mask='circle'
)

grey = visual.GratingStim(
            win=win, size=15, units='pix', pos=[0,0],
            sf=0, color='gray',mask='circle'
)

beep = sound.Sound('A', secs=0.5)

#==========================
# Define the trial sequence
#==========================

trial_list = []
trial_list.append({"condition": "signal", "correct_response": "a"})
trial_list.append({"condition": "noise", "correct_response": "d"})

trials = data.TrialHandler(trial_list,nReps=n_trials, extraInfo=exp_info,
                           method='random', originPath=datapath)

#=====================
# Start the experiment
#=====================

start_message.draw()
win.flip()
keys = event.waitKeys(keyList=['space', 'escape'])

instructions.draw()
win.flip()
keys = event.waitKeys(keyList=['space', 'escape'])

# Initialize clocks:
rt_clock = core.Clock() # for response times
change_clock = core.Clock() # for changing stimuli

# Go through the trials
for trial in trials:

    change_clock.reset()
    wait_for = np.random.uniform(2,4)
    now = ptb.GetSecs()
    beep.play(when=now + wait_for)

    while change_clock.getTime() <= wait_for:

        n.draw() # draw noise in the background
        grey.draw()
        pretrial.draw()
        win.flip()

    if trial['condition']=="signal":
        n.draw() # draw noise in the background
        s.draw() # draw grating on top of noise
        grey.draw()
        fixation.draw()
        win.flip()
    else:
        n.draw() # draw noise in the background
        grey.draw()
        fixation.draw()
        win.flip()

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
            trials.addData('resp_key', resp_key[0])
            timeout = 0

    change_clock.reset()

    # intertrial interval
    while change_clock.getTime() <= changetime:
        n.draw() # draw noise in the background
        grey.draw()
        intertrial.draw()
        win.flip()

    # Add the current trial's data to the TrialHandler
    trials.addData('rt', rt)
    trials.addData('timeout', timeout)

    # Go to the next trial

#======================
# End of the experiment
#======================

# Save all data to a file
trials.saveAsWideText(data_fname + '.csv', delim=',')

change_clock.reset()

while change_clock.getTime() <= 3:
    thanks.draw()
    win.flip()

# Quit the experiment
win.close()
core.quit()
