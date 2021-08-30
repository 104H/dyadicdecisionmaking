import sys
import os
import json
import time
import numpy as np
import psychopy
from psychopy import visual, event, core, monitors, data
import stimuli
from psychopy.sound import Sound

# Directory Specs
HOME = os.getcwd()
DATA = '/data/'

# monitor specs global variables
M_WIDTH = stimuli.M_WIDTH
M_HEIGHT = stimuli.M_HEIGHT
REFRESH_RATE = stimuli.REFRESH_RATE

myMon = monitors.Monitor('DellU2412M', width=M_WIDTH, distance=80)
myMon.setSizePix([M_WIDTH, M_HEIGHT])

# Subject data dictionary
subjectData = {'pair_id': [], 'titration_counter': [], 'chamber':[], 'threshold': [], 'threshold_list': [] }

# get pair id via command-line argument
try:
    #pair_id=200
    pair_id = int(sys.argv[1])
except:
    print('Please enter a number as pair id as command-line argument!')
    pair_id = input()

subjectData['pair_id'] = pair_id

chamber = []
#chamber=1
while chamber == []:
    print("Enter chamber number (1 or 2):")
    chamber = input()

    if chamber not in ["1", "2"]:
        print("Wrong. Enter chamber number (1 or 2):")
        continue

subjectData['chamber'] = chamber

# variables for button box input
keys = ["2", "1"] if chamber == "1" else ["7", "8"] # first one is yes

# the screen
window = psychopy.visual.Window(size=(M_WIDTH, M_HEIGHT), units='pix', screen=int(chamber), fullscr=False, pos=None, blendMode='add', useFBO=True, monitor=myMon)
window.mouseVisible = False

# the stimulus
stimulus = stimuli.stim(window=window, xoffset=0, threshold=0.2)
signal = stimulus.signal
noise = stimulus.noise
reddot = stimulus.reddot

beep = Sound('A', secs=0.5, volume=0.1)

# display instructions and wait
key = []
while not key:
    visual.TextStim(window,
                        text="Press yes (2 or 7) to start", pos=(0, 0),
                        color='black', height=20).draw()
    window.flip()
    key = event.waitKeys(keyList=keys[:1])

# stimulus draw function
def draw_stim(noise, signal, reddot):
    noise = stimulus.updateNoise()
    noise.draw()
    signal.draw()
    reddot.draw()

def secondstoframes (seconds):
    return range( int( np.rint(seconds * REFRESH_RATE) ) )


# create the staircase handler
staircase = data.StairHandler(startVal = 0.1, nReversals=10,
                          stepType = 'log', stepSizes=[0.08,0.04,0.04,0.02],
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=20, minVal=0, maxVal=1)

# do the titration
contrastList = []
responses = []
trial = 0

for thisIncrement in staircase:  # will continue the staircase until it terminates!

    trial+=1
    # set contrast of stimulus
    signal.opacity = thisIncrement
    contrastList.append(thisIncrement)

    # draw noise for 4-6 seconds
    for _ in secondstoframes( np.random.uniform(6, 4) ):
        noise = stimulus.updateNoise()
        noise.draw()
        reddot.draw()
        window.flip()

    event.clearEvents()
    beep.play()
    # get response
    thisResp = None
    key = []
    while not key:
        draw_stim(noise, signal, reddot)
        window.flip()
        key = event.getKeys(keyList=keys)

    if keys[1] in key: # if they didn't see it
        thisResp = 0
        responses.append(thisResp)
    elif keys[0] in key:
        thisResp = 1
        responses.append(thisResp)
    else:
        print("Wrong key!")

    beep.stop()
    event.clearEvents()

    # add the data to the staircase so it can calculate the next level
    staircase.addData(thisResp)


# show end screen
instructions = "You have finished the titration.\n\n\
Please wait"
visual.TextStim(window,
                text=instructions, pos=(0, 0),
                color='black', height=20).draw()
window.flip()
core.wait(5)
window.close()

    #staircase_means.append(staircase.quantile(0.5))
    #staircase.addResponse(response)


print('reversals:')
print(staircase.reversalIntensities)
approxThreshold = np.average(staircase.reversalIntensities[-6:])
print('mean of final 6 reversals = %.3f' % (approxThreshold))

# fill subject dictionary with threshold and staircase value list
subjectData['threshold'] = approxThreshold
subjectData['threshold_list'] = contrastList

print('The shown contrast values are: ')
for member in contrastList:
    print("%.4f" % member)

print("responses: ")
print(responses)
print("number of trials: ")
print(trial)

# Create directory and save as JSON
DATAPATH = HOME+DATA+str(pair_id)
if not os.path.exists(DATAPATH):
    os.makedirs(DATAPATH)
    os.chdir(DATAPATH)
    with open('data_chamber'+str(chamber)+'.json', 'w') as fp:
        json.dump(subjectData, fp)
