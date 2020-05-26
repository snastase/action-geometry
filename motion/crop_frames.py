#!/bin/usr/env python

from skimage import io
from glob import glob
from os.path import join

base_dir = '/home/nastase/social_actions/motion'
frames_dir = join(base_dir, 'frames')
cropped_dir = join(base_dir, 'cropped_frames')

frame_fns = glob(join(frames_dir, '*/frame_001.png'))
frames = [fn.strip().split('/')[-2][:-6] for fn in frame_fns]

for fn, frame in zip(frame_fns, frames):
    image = io.imread(fn)
    crop_dim = (image.shape[1] - image.shape[0]) / 2
    cropped = image[:, crop_dim:-crop_dim, :]
    assert cropped.shape[0] == cropped.shape[1]
    io.imsave(join(cropped_dir, frame + '_cropped_frame_001.png'), cropped)
