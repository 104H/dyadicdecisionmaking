from psychopy import visual, core, event, tools, monitors
import numpy as np
import math

# open window
win = visual.Window([1024,768],units='pix',blendMode='avg',fullscr=False)

mon = monitors.Monitor('testMonitor')

def next_power_of_2(x):
    return int(math.pow(2.0,math.ceil(math.log(x)/math.log(2.0))))

# stimuli setup
stim_size = next_power_of_2(tools.monitorunittools.deg2pix(5,mon)) # has to be a square power of two (e.g. 256, 512, etc.) to use for textures in PsychoPy

sf = 2/tools.monitorunittools.deg2pix(1,mon) # spatial frequency, has to be two cycles per degree as in the original study

# fixation dot
fixation = visual.GratingStim(win=win, size=3, units='pix', pos=[0,0], sf=0, color=[1.0, -1.0, -1.0],mask='circle')

annulus = visual.GratingStim(
    win = win, mask = 'circle', tex = np.zeros((64,64)),
    size = 50, contrast = 1.0, opacity = 1.0,
)

gabortexture = (
    visual.filters.makeGrating(res=stim_size, cycles=stim_size * sf) *
    visual.filters.makeMask(matrixSize=stim_size, shape="circle", range=[0, 1])
)

signal = visual.GratingStim(
    win = win, blendmode='add', tex = gabortexture, mask = 'circle',
    size = stim_size, contrast = 1.0, opacity = 0.5,
)

noise = visual.NoiseStim(
    win=win, mask='circle', ori=1.0, pos=(0,0),
    size=stim_size, sf=None, phase=0, color=[1,1,1], colorSpace='rgb', opacity=1,
    blendmode='add', contrast=0.2, texRes=512, filter='None',noiseType='Uniform',
    noiseElementSize=1, noiseBaseSf=32.0/512, noiseBW=1.0, noiseBWO=30,
    noiseFractalPower=-1,noiseFilterLower=3/512, noiseFilterUpper=8.0/512.0,
    noiseFilterOrder=3.0, noiseClip=3.0, interpolate=False, depth=-1.0
)

# display signal for 600 frames
for frame in range(600):
    noise.draw()
    noise.updateNoise() # update noise on every frame
    signal.draw()
    annulus.draw()
    fixation.draw()
    win.flip()

# display noise until any key is pressed
while not event.getKeys():
    noise.draw()
    noise.updateNoise() # update noise
    annulus.draw()
    fixation.draw()
    win.flip()

win.close()
core.quit()
