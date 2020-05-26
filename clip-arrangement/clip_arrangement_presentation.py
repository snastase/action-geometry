#!/usr/bin/env python

from os.path import join
import time
from psychopy import core, event, logging, visual
from mvpa2.base.hdf5 import h5load, h5save

participant = 1
session = 1
n_subsets = 12
subset_size = 30

subsets = h5load('arrangements/starting_arrangements_n{0}_r{1}_p{2}_s{3}.hdf5'.format(
                    subset_size, n_subsets, participant, session))

clock = core.Clock()
logging.setDefaultClock(clock)
log = logging.LogFile(f=join('logs', 'arrangement_log_p{0}_s{1}.txt'.format(
                participant, session)), level=logging.DATA,
                filemode='w')

win = visual.Window(size=(1920, 1200), color=(0, 0, 0), fullscr=True,
                    screen=1, units='pix')

instructions_text = ("You will be shown sets of images on the screen. "
                     "Each image is a screenshot corresponding to one of "
                     "the video clips you've seen before. The images "
                     "represent their corresponding clips. All of the "
                     "images start outside the circle. You should "
                     "move the images around inside the circle so that "
                     "clips that are similar to each other in terms of "
                     "the social interaction depicted are close. The more "
                     "similar the two clips are in terms of social content, "
                     "the closer the images should be. Left-click "
                     "and drag to move the images; right-click to play "
                     "the corresponding clip. Do not drag the images too "
                     "fast and try not to leave them completely overlapping. "
                     "When you're finished, make sure all the images are "
                     "inside the circle, then press 'spacebar' to finalize "
                     "your arrangement. The first trial will have all 90 "
                     "clips, while the subsequent trials will have smaller "
                     "subsets. Press 'spacebar' to begin.")

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
    if 'space' in keys or 'enter' in keys:
        start = True
    if 'q' in keys or 'escape' in keys:
        win.close()
        core.quit()

radius = 500

arena = visual.Circle(win, radius=(radius, radius), units='pix', edges=100,
                      lineWidth=10.0, interpolate=True)

logging.data("Starting experiment!")
results = {}
for subset_i, subset in enumerate(subsets):
    loading.draw()
    arena.draw()
    win.flip()

    starting_positions = {stimulus: [s * (radius + 60) for s in start_position]
                          for stimulus, start_position in subset}

    frames = {stimulus: visual.ImageStim(win, image=join('stimuli', 'frames',
                                              stimulus + '_cropped_frame_001.png'),
                               size=(72, 72), units='pix',
                               pos=[s * (radius + 60) for s in start_position],
                               name=stimulus)
              for stimulus, start_position in subset}

    for frame in frames.values():
        frame.draw()
    win.flip()
    logging.data("Finished drawing images, starting trial {0}!".format(subset_i))

    finished = False
    while not finished:
        arena.draw()
        for frame in frames.values():
            frame.draw()
        win.flip()

        for stimulus, frame in frames.items():
            while mouse.isPressedIn(frame, buttons=[0]):
                position = mouse.getPos()
                frame.pos = position
                arena.draw()
                frame.draw()
                for other_stimulus, other_frame in frames.items():
                    if other_stimulus != stimulus:
                        other_frame.draw()
                win.flip()
       
        for stimulus, frame in frames.items(): 
            if mouse.isPressedIn(frame, buttons=[2]):
                clip = visual.MovieStim(win, filename=join('stimuli', 'clips',
                                                           stimulus + '_final.mp4'),
                                        size=(256, 144), pos=frame.pos, name='Clip')
                start_time = time.time()
                clip.play()
                while time.time() - start_time <= 2.5:
                    arena.draw()
                    for frame in frames.values():
                        frame.draw()
                    clip.draw()
                    win.flip()

        keys = event.getKeys()
        if 'space' in keys or 'enter' in keys:
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
                    h5save('arrangements/final_arrangements_n{0}_r{1}_p{2}_s{3}.hdf5'.format(
                                subset_size, n_subsets, participant, session), results)
                    win.close()
                    core.quit()

logging.data("Completed experiment, saving results!")
complete = visual.TextStim(win, text=("Experiment complete. Thanks!"),
                          wrapWidth=950, name="Complete")
complete.height = 36
complete.draw()
win.flip()
h5save('arrangements/final_arrangements_n{0}_r{1}_p{2}_s{3}.hdf5'.format(
       subset_size, n_subsets, participant, session), results)

end_experiment = False
while not end_experiment:
    complete.draw()
    win.flip()
    keys = event.getKeys()
    if 'q' in keys or 'escape' in keys:
        win.close()
        core.quit()
