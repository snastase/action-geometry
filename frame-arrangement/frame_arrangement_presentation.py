#!/usr/bin/env python
# run using "frame_arrangement_presentation.py 1 1 person"

import sys
import json
from collections import OrderedDict
from os.path import join
import time
from psychopy import core, event, logging, visual
from mvpa2.base.hdf5 import h5load, h5save

participant = int(sys.argv[1])
session = int(sys.argv[2])
task = sys.argv[3]
n_subsets = 12
subset_size = 30

assert session in [3, 4, 5]
assert task in ['person', 'object', 'scene']

subsets = h5load('arrangements/starting_frame_arrangements_n{0}_r{1}_p{2}_s{3}.hdf5'.format(
                    subset_size, n_subsets, participant, session))

clock = core.Clock()
logging.setDefaultClock(clock)
log = logging.LogFile(f=join('logs', 'arrangement_log_p{0}_s{1}.txt'.format(
                participant, session)), level=logging.DATA,
                filemode='w')
logging.data("Arrangements for participant {0}, session {1}, "
             "{2} task, with {3} subsets of {4} items".format(
                participant, session, task, n_subsets, subset_size))
win = visual.Window(size=(1920, 1200), color=(0, 0, 0), fullscr=True,
                    screen=1, units='pix')

if task == 'person':
    instructions_text = ("You will be shown sets of images on the screen. "
                         "All of the images start outside the circle. Move "
                         "the images into the circle and organize them so "
                         "that images depicting similar people are nearest "
                         "to each other. The more similar the people, the "
                         "closer the images should be. We've highlighted the "
                         "person's (or people's) face and body in each image. "
                         "Right-click on an "
                         "image to select it, then left-click at the desired "
                         "location to move it. Left-click and drag to make "
                         "additional adjustments. Click the middle mouse "
                         "button (scroll-wheel) to view a larger version of "
                         "the image. When you're finished, make sure all the "
                         "images are inside the circle, then press 'spacebar' "
                         "to finalize your arrangement. The first trial will "
                         "have all 90 images, while the subsequent trials will "
                         "have smaller subsets. Press 'spacebar' to begin.")

elif task == 'object':
    instructions_text = ("You will be shown sets of images on the screen. "
                         "All of the images start outside the circle. Move "
                         "the images into the circle and organize them so "
                         "that images depicting similar objects are nearest "
                         "to each other. The more similar the objects, the "
                         "closer the images should be. We've highlighted the "
                         "relevant object(s) in each image. Right-click on an "
                         "image to select it, then left-click at the desired "
                         "location to move it. Left-click and drag to make "
                         "additional adjustments. Click the middle mouse "
                         "button (scroll-wheel) to view a larger version of "
                         "the image. When you're finished, make sure all the "
                         "images are inside the circle, then press 'spacebar' "
                         "to finalize your arrangement. The first trial will "
                         "have all 90 images, while the subsequent trials will "
                         "have smaller subsets. Press 'spacebar' to begin.")

elif task == 'scene':
    instructions_text = ("You will be shown sets of images on the screen. "
                         "All of the images start outside the circle. Move "
                         "the images into the circle and organize them so "
                         "that images depicting similar scenes or places are "
                         "nearest to each other. The more similar the "
                         "scenery, the closer the images should be. We've "
                         "highlighted the scenery in each image. Right-click on an "
                         "image to select it, then left-click at the desired "
                         "location to move it. Left-click and drag to make "
                         "additional adjustments. Click the middle mouse "
                         "button (scroll-wheel) to view a larger version of "
                         "the image. When you're finished, make sure all the "
                         "images are inside the circle, then press 'spacebar' "
                         "to finalize your arrangement. The first trial will "
                         "have all 90 images, while the subsequent trials will "
                         "have smaller subsets. Press 'spacebar' to begin.")

instructions = visual.TextStim(win, text=instructions_text, wrapWidth=1100,
                               pos=(0, 0), alignHoriz='center',
                               alignVert='center', name='Instructions')
instructions.height = 36
instructions.draw()
win.flip()

finished_prompt = visual.TextStim(win, text=("Are you sure you're finished? "
                                             "(press 'y' or 'n')"),
                                  wrapWidth=950, name="Finished?")
finished_prompt.height = 36
quit_prompt = visual.TextStim(win, text=("Are you sure you want to quit? "
                                         "(press 'y' or 'n')"),
                              wrapWidth=950, name="Quit?")
quit_prompt.height = 36
loading = visual.TextStim(win, text=("Loading..."),
                          wrapWidth=950, name="Loading")
loading.height = 36

mouse = event.Mouse()

start = False
while not start:
    instructions.draw()
    win.flip()
    keys = event.getKeys()
    if 'space' in keys or 'return' in keys:
        start = True
    if 'q' in keys or 'escape' in keys:
        win.close()
        core.quit()

radius = 500

arena = visual.Circle(win, radius=(radius, radius), units='pix', edges=100,
                      lineWidth=10.0, interpolate=True)

if task == 'person':
    reminder = visual.TextStim(win, text=("Organize clips according\n"
                                          "to people"),
                               pos=(-920, 560), alignHoriz='left',
                               alignVert='top')
elif task == 'object':
    reminder = visual.TextStim(win, text=("Organize clips according\n"
                                          "to objects"),
                               pos=(-920, 560), alignHoriz='left',
                               alignVert='top')
elif task == 'scene':
    reminder = visual.TextStim(win, text=("Organize clips according\n"
                                          "to scenes"),
                               pos=(-920, 560), alignHoriz='left',
                               alignVert='top')

logging.data("Starting experiment!")
results = {}
for subset_i, subset in enumerate(subsets):
    loading.draw()
    reminder.draw()
    arena.draw()
    win.flip()

    starting_positions = {stimulus: [s * (radius + 60) for s in start_position]
                          for stimulus, start_position in subset}
    if subset_i == 0:
        frames = OrderedDict({stimulus: visual.ImageStim(win, image=join('stimuli', 'frames',
                                                  stimulus + '_frame001_{0}.png'.format(task)),
                                   size=(60, 60), units='pix',
                                   pos=[s * (radius + 60) for s in start_position],
                                   name=stimulus)
                  for stimulus, start_position in subset})
    elif subset_i > 0:
        frames = OrderedDict({stimulus: visual.ImageStim(win, image=join('stimuli', 'frames',
                                                  stimulus + '_frame001_{0}.png'.format(task)),
                                   size=(72, 72), units='pix',
                                   pos=[s * (radius + 60) for s in start_position],
                                   name=stimulus)
                  for stimulus, start_position in subset})

    for frame in frames.values():
        frame.draw()
    win.flip()
    logging.data("Finished drawing images, starting trial {0}!".format(subset_i))

    finished = False
    while not finished:
        arena.draw()
        reminder.draw()
        for frame in frames.values():
            frame.draw()
        win.flip()

        was_dragged = None
        for stimulus, frame in frames.items()[::-1]:
            while mouse.isPressedIn(frame, buttons=[0]) or (was_dragged and mouse.getPressed()[0] == 1):
                if not was_dragged:
                    frames[stimulus] = frames.pop(stimulus)
                    was_dragged = frame
                position = mouse.getPos()
                frame.pos = position
                arena.draw()
                reminder.draw()
                for other_stimulus, other_frame in frames.items():
                    if other_stimulus != stimulus:
                        other_frame.draw()
                frame.draw()
                win.flip()
            if was_dragged:
                break
        
        for stimulus, frame in frames.items()[::-1]:
            if mouse.isPressedIn(frame, buttons=[2]):
                second_click = False
                while not second_click:
                    mouse.clickReset()
                    buttons = mouse.getPressed()
                    if buttons[0] == 1:
                        position = mouse.getPos()
                        second_click = True
                    else:
                        highlight = visual.Rect(win, fillColor='white',
                                        width=frame.size[0] + 6,
                                        height=frame.size[1] + 6, 
                                        pos=frame.pos)
                        arena.draw()
                        reminder.draw()
                        for other_stimulus, other_frame in frames.items():
                            if other_stimulus != stimulus:
                                other_frame.draw()
                        highlight.draw()
                        frame.draw()
                        win.flip()
                frame.pos = position
                arena.draw()
                reminder.draw()
                for other_stimulus, other_frame in frames.items():
                    if other_stimulus != stimulus:
                        other_frame.draw()
                frame.draw()
                win.flip()
       
        for stimulus, frame in frames.items()[::-1]: 
            if mouse.isPressedIn(frame, buttons=[1]):
                zoomed = visual.ImageStim(win, image=join('stimuli', 'frames',
                                                  stimulus + '_frame001_{0}.png'.format(task)),
                                   size=(256, 144), units='pix', pos=frame.pos,
                                   name='Zoomed image')
                while mouse.isPressedIn(zoomed, buttons=[1]):
                    arena.draw()
                    reminder.draw()
                    for frame in frames.values():
                        frame.draw()
                    zoomed.draw()
                    win.flip()

        keys = event.getKeys()
        if 'space' in keys or 'return' in keys:
            responded = False
            while not responded:
                finished_prompt.draw()
                win.flip()
                keys = event.getKeys()
                if 'n' in keys:
                    responded = True
                if 'y' in keys:
                    results[subset_i] = {}
                    for name, stimulus in frames.items():
                        results[subset_i][name] = {}
                        results[subset_i][name]['start'] = starting_positions[name]
                        results[subset_i][name]['finish'] = stimulus.pos.tolist()
                    logging.data("Done trial {0}, recorded results!".format(subset_i))
                    responded = True
                    finished = True
                    
        if 'q' in keys or 'escape' in keys:
            responded = False
            while not responded:
                quit_prompt.draw()
                win.flip()
                keys = event.getKeys()
                if 'n' in keys:
                    responded = True
                if 'y' in keys:
                    fn = 'arrangements/final_arrangements_n{0}_r{1}_p{2}_s{3}'.format(
                                subset_size, n_subsets, participant, session)
                    h5save('{0}.hdf5'.format(fn), results)
                    with open('{0}.json'.format(fn), 'w') as f:
                        json.dump(results, f, indent=2)
                    win.close()
                    core.quit()

logging.data("Completed experiment, saving results!")
complete = visual.TextStim(win, text=("Experiment complete. Thanks!"),
                          wrapWidth=950, name="Complete")
complete.height = 36
complete.draw()
win.flip()
fn = 'arrangements/final_arrangements_n{0}_r{1}_p{2}_s{3}'.format(
            subset_size, n_subsets, participant, session)
h5save('{0}.hdf5'.format(fn), results)
with open('{0}.json'.format(fn), 'w') as f:
    json.dump(results, f, indent=2)

end_experiment = False
while not end_experiment:
    complete.draw()
    win.flip()
    keys = event.getKeys()
    if 'q' in keys or 'escape' in keys:
        win.close()
        core.quit()
