#!/usr/bin/env python

# Run Gallant/Nishimoto/Lescroart MATLAB implementation
# of motion energy model on frames

from os.path import exists, join
from subprocess import call

base_dir = '/home/nastase/social_actions'
scripts_dir = join(base_dir, 'scripts')
motion_dir = join(base_dir, 'motion')
frames_dir = join(motion_dir, 'frames')
output_dir = join(motion_dir, 'output')

with open(join(scripts_dir, 'stimuli.csv')) as f:
    stimuli = sorted([line.strip().split(',')[2][:-4] for line in f.readlines()])

# Run motion energy model
for stimulus in stimuli:
    stim_fn = join(frames_dir, stimulus, 'downsampled', stimulus + '.mat')
    assert exists(stim_fn)

    output_fn = join(output_dir, 'me_' + stimulus + '.mat')

    matlab_cmd = """
                 matlab -nojvm -nodisplay -nosplash -nodesktop -r "fname='{0}'; outname='{1}'; run('{2}'); exit"
                 """.format(stim_fn, output_fn, join(motion_dir, 'snComputeMotionEnergy.m'))
    print matlab_cmd
    call(matlab_cmd, shell=True)
print("Finished running motion energy model")

# Convert back to python and get paired distances
from scipy.io import loadmat
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import seaborn as sns
from mvpa2.base.hdf5 import h5load, h5save
from scipy.stats import rankdata

motion_energy = {}
for stimulus in stimuli:
    me = loadmat(join(output_dir, 'me_' + stimulus + '.mat'))['S_fin']
    motion_energy[stimulus] = me

# Try downsampling to MRI TR or just mean over clip
motion_energy_down = {}
for stimulus, me in motion_energy.items():
    me_down = np.vstack((np.mean(me[:15], axis=0), np.mean(me[15:30], axis=0), np.mean(me[30:], axis=0)))
    motion_energy_down[stimulus] = me_down

# Mean over entire clip
motion_energy_mean = {}
for stimulus, me in motion_energy.items():
    me_mean = np.mean(me, axis=0)
    motion_energy_mean[stimulus] = me_mean

#me_stack = np.vstack([me.ravel() for me in motion_energy.values()])
#me_stack = np.vstack([me.ravel() for me in motion_energy_down.values()])
me_stack = np.vstack([me.ravel() for me in motion_energy_mean.values()])
distances = pdist(me_stack, 'correlation')
h5save('motion_energy_mean_target_RDM.hdf5', distances)

target_RDM = h5load(join(scripts_dir, 'RDMs', 'motion_energy_target_RDM.hdf5'))

condition_order = h5load('/home/nastase/social_actions/scripts/condition_order.hdf5')
reorder, sparse_ordered_labels = condition_order['reorder'], condition_order['sparse_ordered_labels']

plt.figure(figsize=(8, 6))
ax = sns.heatmap(squareform(rankdata(target_RDM) / len(target_RDM) * 100)[reorder][:, reorder], vmin=0, vmax=100,
            square=True, cmap='RdYlBu_r', xticklabels=sparse_ordered_labels, yticklabels=sparse_ordered_labels)
ax.xaxis.tick_top()
plt.xticks(rotation=45, ha='left')
plt.yticks(va='top')
plt.tight_layout()
plt.show()

