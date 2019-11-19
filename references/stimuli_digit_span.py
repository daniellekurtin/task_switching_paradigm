from psychopy import visual, clock, core
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np 
from itertools import product

# Size and color 
stimGridSize = 800 # width and height of the grid
answerGridSize = 200 
gridXY = 6 # number of cells per axis -> number of cells = gridXY**2
colouredboxSize = stimGridSize/gridXY
gridColour = np.array([-0.4,-0.4,-0.4])
stimColour = np.array([-1,-1,-1])

# Stim Grid
cellCoordinates = stimGridSize/gridXY*(gridXY-1)/2
cellCoordinates = np.asarray(list(product(np.linspace(-cellCoordinates,cellCoordinates,gridXY),repeat=2)))
stimGridCoordinates = np.asarray([(l-300,0) for l in  np.linspace((-stimGridSize)/2,(stimGridSize)/2,gridXY+1)] + [(-300,l) for l in np.linspace((-stimGridSize)/2,(stimGridSize)/2,gridXY+1)])
gridAngles = [90]*(gridXY+1) + [0]*(gridXY+1)

# Coloured box stimuli
colouredboxCoordinates = np.asarray([(l-300,0) for l in  np.linspace((-colouredboxSize)/2,(colouredboxSize)/2,gridXY+1)] + [(-300,l) for l in np.linspace((-colouredboxSize)/2,(colouredboxSize)/2,gridXY+1)])

# Answer Grid 
answerCellCoordinates = answerGridSize/gridXY*(gridXY-1)/2
answerCellCoordinates = np.asarray(list(product(np.linspace(-cellCoordinates,cellCoordinates,gridXY),repeat=2)))
answerGrid1Coordinates = np.asarray([(h+500,0) for h in  np.linspace((-answerGridSize)/2,(answerGridSize)/2,gridXY+1)] + [(500,h) for h in np.linspace((-answerGridSize)/2,(answerGridSize)/2,gridXY+1)])
answerGrid2Coordinates = np.asarray([(h+500,250) for h in  np.linspace((-answerGridSize)/2,(answerGridSize)/2,gridXY+1)] + [(500,h+250) for h in np.linspace((-answerGridSize)/2,(answerGridSize)/2,gridXY+1)])
answerGrid3Coordinates = np.asarray([(h+500,-250) for h in  np.linspace((-answerGridSize)/2,(answerGridSize)/2,gridXY+1)] + [(500,h-250) for h in np.linspace((-answerGridSize)/2,(answerGridSize)/2,gridXY+1)])
gridAngles = [90]*(gridXY+1) + [0]*(gridXY+1)

# Visual Stim and Answer Grids
win = visual.Window([1536, 864],winType='pyglet',screen=1,monitor='External Monitor HD',units='pix',fullscr = True, autoLog=False, gammaErrorPolicy='ignore')
win.mouseVisible = False

stimGrid = visual.ElementArrayStim(win=win, name='stimGrid', nElements=(gridXY+1)*2, sizes=[stimGridSize,2], xys = stimGridCoordinates, oris=gridAngles, units='pix', 
            elementTex=np.ones([16,16]), elementMask=np.ones([16,16]), colors=gridColour, colorSpace='rgb', autoLog=False)

answerGrid1 = visual.ElementArrayStim(win=win, name='answerGrid1', nElements=(gridXY+1)*2, sizes=[answerGridSize,2], xys = answerGrid1Coordinates, oris=gridAngles, units='pix', 
            elementTex=np.ones([16,16]), elementMask=np.ones([16,16]), colors=gridColour, colorSpace='rgb', autoLog=False)

answerGrid2 = visual.ElementArrayStim(win=win, name='answerGrid2', nElements=(gridXY+1)*2, sizes=[answerGridSize,2], xys = answerGrid2Coordinates, oris=gridAngles, units='pix', 
            elementTex=np.ones([16,16]), elementMask=np.ones([16,16]), colors=gridColour, colorSpace='rgb', autoLog=False)

answerGrid3 = visual.ElementArrayStim(win=win, name='answerGrid3', nElements=(gridXY+1)*2, sizes=[answerGridSize,2], xys = answerGrid3Coordinates, oris=gridAngles, units='pix', 
            elementTex=np.ones([16,16]), elementMask=np.ones([16,16]), colors=gridColour, colorSpace='rgb', autoLog=False)

# Visual Colored boxes and numbers
#colouredbox = visual.ElementArrayStim(win=win, name='colouredbox', nElements=1, sizes=[colouredboxSize,2], xys=colouredboxCoordinates, oris=0, units='pix', 
            #elementTex=None, elementMask='circle', colors=stimColour, colorSpace='rgb', autoLog=False)

# Initialize components for Routine "Instruction"
InstructionClock = core.Clock()
instruction = visual.TextStim(win=win, name='instruction',
    text='Press any key to start',
    font='Arial',
    pos=(0, 0), height=50, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0)

#instruction.draw()
#win.flip()
#clock.wait(2)

stimGrid.draw()
win.flip()
clock.wait(2)

stimGrid.draw()
#colouredbox.draw()
win.flip()
clock.wait(2)

#stimGrid.draw()
#answerGrid1.draw()
#answerGrid2.draw()
#answerGrid3.draw()
#win.flip()
#clock.wait(2)