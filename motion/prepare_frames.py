#!/bin/usr/env python

from os.path import exists, join
from os import makedirs
from subprocess import call
import numpy as np
from skimage import color, io, transform
from scipy.io import savemat
from glob import glob
from scipy.interpolate import interp1d

base_dir = '/home/nastase/social_actions'
stim_dir = join(base_dir, 'experiment', 'stimuli')
scripts_dir = join(base_dir, 'scripts')
motion_dir = join(base_dir, 'motion')

with open(join(scripts_dir, 'stimuli.csv')) as f:
    stim_fns = sorted([line.strip().split(',')[2] for line in f.readlines()])

with open(join(motion_dir, 'framerates.txt')) as f:
    framerates = {line.strip().split(',')[0]: float(line.strip().split(',')[1])
                    for line in f.readlines()}

for stimulus in stimuli:
    stim_fn = join(frames_dir, 'stimulus', 'downsampled', stim_fn+'.mat')
    print stim_fn
    assert exists(stim_fn)
for stim_fn in stim_fns:
    stim_path = join(stim_dir, stim_fn)
    frames_dir = join(motion_dir, 'frames', stim_fn[:-4])
    if not exists(frames_dir):
        makedirs(frames_dir)
    frames_path = join(frames_dir, 'frame_%03d.png')
    call("ffmpeg -i {0} {1} -hide_banner".format(stim_path, frames_path),
            shell=True)

for stim_fn in stim_fns:
    print("Downsampling clip {0}".format(stim_fn))
    frames_dir = join(motion_dir, 'frames', stim_fn[:-4])
    frames_fns = sorted(glob(join(frames_dir, 'frame_*.png')))

    downsampled_dir = join(frames_dir, 'downsampled')
    if not exists(downsampled_dir):
        makedirs(downsampled_dir)

    n_frames = int(np.round(framerates[stim_fn] * 2.5))
    print("Based on framerate, using {0} frames".format(n_frames))
    
    downsampled_frames = []
    for frame_i in range(1, n_frames + 1):
        image = io.imread(join(frames_dir, 'frame_{0:0>3}.png'.format(frame_i)))
        #assert image.shape == (720, 1280, 3)
        pad = (image.shape[1] - image.shape[0]) / 2
        background = np.zeros((pad, image.shape[1], 3), dtype='uint8') + 128
        square = np.vstack((background, image, background)).astype('uint8')
        assert square.shape[0] == square.shape[1]
        downsampled = transform.resize(square, (96, 96), order=0,
                        preserve_range=True).astype('uint8')
        downsampled_frames.append(downsampled)
        io.imsave(join(downsampled_dir, 'frame_{0:0>3}.png'.format(frame_i)), downsampled)

    downsampled_array = np.transpose(np.array(downsampled_frames), (1, 2, 3, 0))

    xp = np.arange(0, downsampled_array.shape[-1], downsampled_array.shape[-1]/37.)
    lin = interp1d(np.arange(downsampled_array.shape[-1]), downsampled_array, kind='nearest', axis=-1)
    downsampled_15fps = lin(xp)
    assert downsampled_15fps.shape[-1] == 37

    print image.shape, square.shape, downsampled_array.shape, downsampled_15fps.shape
    savemat(file(join(downsampled_dir, stim_fn[:-4] + '.mat'), 'w'), {'S': downsampled_15fps})
