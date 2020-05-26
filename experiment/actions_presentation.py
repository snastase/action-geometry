#!/usr/bin/env python

# Run this from the command line from 'actions' directory using:
#   python actions_presentation.py

# Optionally supply DBIC ID, accession number, and participant number:
#   python actions_presentation.py <DBIC ID> <accession number> <participant_number>
# Command line arguments must be in order!

import sys
import time
import serial
import multiprocessing
from os.path import exists, join
from psychopy import core, event, gui, logging, visual
from psychopy.hardware.emulator import launchScan
from mvpa2.base.hdf5 import h5load, h5save

# Set up GUI for inputing participant/run information (with defaults)
if len(sys.argv) > 1:
    DBIC_ID = sys.argv[1]
    accession = sys.argv[2]
    participant = sys.argv[3]
else:
    DBIC_ID = "e.g., SID000001"
    accession = "e.g., A000001"
    participant = "e.g., 1"

run_configuration = gui.Dlg(title='Run configuration')
run_configuration.addField("DBIC ID:", DBIC_ID)
run_configuration.addField("Scan accession number:", accession)
run_configuration.addField("Participant:", participant)
run_configuration.addField("Scanning session:")
run_configuration.addField("Run number:")
run_configuration.show()

if run_configuration.OK:
    DBIC_ID = run_configuration.data[0]
    accession = run_configuration.data[1]
    participant = int(run_configuration.data[2])
    session = int(run_configuration.data[3])
    run = int(run_configuration.data[4])
elif not run_configuration.OK:
    core.quit()

# Start PsychoPy's clock (mostly for logging)
run_clock = core.Clock()

# Set up PsychoPy's logging function
logging.setDefaultClock(run_clock)
log = logging.LogFile(f=join('logs', 'log_p{0}_s{1}_r{2}.txt'.format(
                participant, session, run)), level=logging.INFO,
                filemode='w')

# Load in events / trial order
trials = h5load(join('trial_orders',
                     'trial_order_p{0}_s{1}_r{2}.hdf5'.format(
                         participant, session, run)))
assert len(trials) == 100 + 3

# Open window and wait for first scanner trigger
win = visual.Window([1280, 1024], screen=1, fullscr=True, color=0, name='Window')

instructions = visual.TextStim(win, pos=[-.9, .9], wrapWidth=1.8,
        alignHoriz='left', alignVert='top', name='Instructions',
                text=("Watch the following clips and pay attention "
                      "to the actions depicted in each clip. "
                      "Occasionally you will be asked to respond to "
                      "a question about the preceding clip. "
                      "Press the button on the side corresponding "
                      "to the correct answer. Question format:"))
question_text = ("Which of these two verbs is most\n"
                 "    closely related to the action\n"
                 "  depicted in the preceding clip?")
question_example = visual.TextStim(win, text=question_text, pos=(0, -.25), alignHoriz='center',
                           alignVert='bottom', wrapWidth=2, name='Question example')
probe_left_example = visual.TextStim(win, text='"verb"', pos=(-.35, -.5),
                                     alignHoriz='center', alignVert='center',
                                     name='Left probe example: "verb"')
probe_right_example = visual.TextStim(win, text='"verb"', pos=(.35, -.5),
                                      alignHoriz='center', alignVert='center',
                                      name='Right probe example: "verb"')
instructions.draw()
question_example.draw()
probe_left_example.draw()
probe_right_example.draw()
win.flip()

instructions_wait = True
while instructions_wait:
    keys = event.getKeys()
    if 'space' in keys or 'return' in keys:
        logging.info("Finished instructions")
        instructions_wait = False
    if 'q' in keys or 'escape' in keys:
        quitting = ('Quit command ("q" or "escape") was detected! '
                    'Quitting experiment')
        logging.info(quitting)
        print(quitting)
        win.close()
        core.quit()
    
waiting = visual.TextStim(win, pos=[0, 0], text="Waiting for scanner...",
                          name="Waiting")
waiting.draw()
win.flip()

serial_path = '/dev/ttyUSB0'
if not exists(serial_path):
    serial_exists = False
    no_serial = "No serial device detected, using keyboard"
    logging.info(no_serial)
    print(no_serial)
    scanner_wait = True
    while scanner_wait:
        waiting.draw()
        win.flip()
        keys = event.getKeys()
        if '5' in keys:
            scanner_wait = False
        if 'q' in keys or 'escape' in keys:
            quitting = ('Quit command ("q" or "escape") was detected! '
                        'Quitting experiment')
            logging.info(quitting)
            print(quitting)
            win.close()
            core.quit()
elif exists(serial_path):
    serial_exists = True
    found_serial = "Serial device detected"
    logging.info(found_serial)
    print(found_serial)
    ser = serial.Serial(serial_path, 115200, timeout=.0001)
    ser.flushInput()
    while ser.read() != '5':
        waiting.draw()
        win.flip()
        if 'q' in keys or 'escape' in keys:
            quitting = ('Quit command ("q" or "escape") was detected! '
                        'Quitting experiment')
            logging.info(quitting)
            print(quitting)
            win.close()
            core.quit()
    ser.close()

# Set run start time and reset PsychoPy's core.Clock() on first trigger
first_trigger = "Got first scanner trigger! Resetting clocks"
run_start = time.time()
run_clock.reset()
logging.info(first_trigger)

# Start fixation after scanner trigger
fixation = visual.TextStim(win, pos=(0, 0), text="+", name="Fixation")
fixation.draw()
win.flip()

# Start looping through trials
for trial in trials:
    onset = trial[0]

    loaded_clip = False
    if serial_exists:
        ser = serial.Serial(serial_path, 115200, timeout=.0001)
        ser.flushInput()
        
    while time.time() - run_start < onset:
        fixation.draw()
        win.flip()
        
        if serial_exists:
            serial_input = ser.read()
            if len(list(serial_input)) > 0:
                if '5' in serial_input:
                    logging.info('Scanner trigger received')
                if '1' in serial_input:
                    logging.data('Serial response 1')
                if '2' in serial_input:
                    logging.data('Serial response 2')

        keys = event.getKeys(timeStamped=run_clock)
        for key in keys:
            logging.data(key)
            if key[0] == '5':
                logging.info('Scanner trigger received from keyboard')
            if key[0] in ('q', 'escape'):
                quitting = ('Quit command ("q" or "escape") was detected! '
                            'Quitting experiment')
                logging.info(quitting)
                print(quitting)
                win.close()
                core.quit()

        if trial[2] != 'fixation' and trial[2] != 'question' and not loaded_clip:
            clip_fn = join('stimuli', trial[2])
            clip = visual.MovieStim2(win, clip_fn, size=720,
                                     pos=(0, 0), flipVert=False,
                                     flipHoriz=False, loop=False,
                                     noAudio=True, name=trial[2])
            loaded_clip = True
    
    trial_start = time.time()
    if trial[2] == 'fixation':
        while time.time() - trial_start <= 2.5:
            fixation.draw()
            win.flip()

    elif trial[2] == 'question':
        #question = visual.TextStim(win, text=question_text, pos=(0, .25), alignHoriz='center',
        #                           alignVert='bottom', wrapWidth=2, name='Question')
        probe_left = visual.TextStim(win, text='"'+trial[3][0]+'"', pos=(-.35, 0),
                                     alignHoriz='center', alignVert='center',
                                     name='Left probe: "{0}"'.format(trial[3][0]))
        probe_right = visual.TextStim(win, text='"'+trial[3][1]+'"', pos=(.35, 0),
                                      alignHoriz='center', alignVert='center',
                                      name='Right probe: "{0}"'.format(trial[3][1]))
        while time.time() - trial_start <= 2.5:
            #question.draw()
            probe_left.draw()
            probe_right.draw()
            win.flip()

    else:
        # Play video for 2.5 s with Psychopy's suggested CPU break
        shouldflip = clip.play()
        while time.time() - trial_start <= 2.5:
            if shouldflip:
                # Movie has already been drawn , so just draw text stim and flip
                win.flip()
            else:
                # Give the OS a break if a flip is not needed
                time.sleep(0.001)
                # Drawn movie stim again. Updating of movie stim frames as necessary
                # is handled internally.
            shouldflip = clip.draw()

while time.time() - run_start <= 535.:
    fixation.draw()
    win.flip()

finished = "Finished run successfully!"
logging.info(finished)
print(finished)

win.close()
core.quit()
