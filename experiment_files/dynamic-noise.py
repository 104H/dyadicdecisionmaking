from psychopy import visual, core, event
import numpy as np

# open window
win = visual.Window([1024,768],units='pix',blendMode='avg')

# fixation dot
fixation = visual.GratingStim(win=win, size=3, units='pix', pos=[0,0], sf=0, color=[1.0, -1.0, -1.0],mask='circle')

annulus = visual.GratingStim(
    win = win, mask = 'circle', tex = np.zeros((64,64)),
    size = 50, contrast = 1.0, opacity = 1.0,
)

noise = visual.NoiseStim(
    win=win, mask='circle', ori=1.0, pos=(0,0),
    size=(512, 512), sf=None, phase=0, color=[1,1,1], colorSpace='rgb', opacity=1,
    blendmode='add', contrast=1.0, texRes=512, filter='None',noiseType='Uniform',
    noiseElementSize=1, noiseBaseSf=32.0/512, noiseBW=1.0, noiseBWO=30,
    noiseFractalPower=-1,noiseFilterLower=3/512, noiseFilterUpper=8.0/512.0,
    noiseFilterOrder=3.0, noiseClip=3.0, interpolate=False, depth=-1.0
)

while not event.getKeys():
    noise.draw()
    noise.updateNoise() # update noise on every frame
    annulus.draw()
    fixation.draw()
    win.flip()

win.close()
core.quit()
