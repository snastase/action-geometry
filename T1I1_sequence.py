
# coding: utf-8

# We use the sequence generator from Geoffrey Aguirre's lab (https://cfn.upenn.edu/aguirre/wiki/public:web-based_sequence_evaluator) to generate the Type 1 Index 1 sequence of stimuli. We have 20 stimulus categories plus a null fixation trial and a catch trial (semantic question), totaling 22 trial categories.

# In[1]:

import numpy as np
from scipy.spatial.distance import squareform
from evalseqshard import EvaluateSeqshard, vec2sim
import matplotlib.pyplot as plt


# In[2]:

# Participant number for random seed
participant = 1


# In[14]:

# Create dictionary of parameters for EvaluateSeqshard function
parameters = {'N': 22,
              'perms': 10000,
              'TrialDuration': 5,
              'BlankLength': 1,
              'doubleblanks': False,
              'target': 21,
              'numSeqs': 100}


# In[15]:

# Simple similarity matrix separating the 20 categories
category_rdm = np.array([[0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1.,],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0.,]])


# In[16]:

# Plot RDM
get_ipython().magic(u'matplotlib inline')
plt.matshow(category_rdm); plt.show()


# In[17]:

# Reformat single RDM for EvaluateSeqshard function
rdms = category_rdm[:, :, None]

# Set seed to get same sequence across runs
np.random.seed(participant)
results = EvaluateSeqshard(parameters, rdms)


# In[18]:

# View condition labels
# 0 = fixation trial, 21 = catch trial
print np.unique(results['BestSeqs'][:, 0])


# In[19]:

# Sort according to the efficiency of the first similarity matrix
sort_idx = np.argsort(results['bestEs'][0, :])[::-1]


# In[20]:

# Sort efficiencies and print first fiew
efficiencies = results['bestEs'][0, sort_idx].T
print efficiencies[:10]


# In[21]:

# Sort sequences and print most efficient
sequences = results['BestSeqs'][:, sort_idx].T
assert len(sequences[0]) == int(parameters['N'])**2 + 1
print sequences[0].shape, sequences[0]


# Each sequence is $22^2 + 1 = 485$ trials long. We'll use two sequences that end with the same trial number per participant.

# In[22]:

# Save efficiencies and sequences
np.savetxt('sequences_{0}.txt'.format(participant),
           sequences, fmt='%d', delimiter=',')
np.savetxt('efficiencies_{0}.txt'.format(participant),
           efficiencies)


# In[23]:

# Find next best sequence with same starting trial
sequence_one = sequences[0]
next_best = np.where(sequences[:, 0] == sequence_one[0])[0][1]
sequence_two = sequences[next_best]
assert not np.array_equal(sequence_one, sequence_two)


# In[24]:

# Print sequences
print "Session one sequence (efficiency = {0}):\n{1}".format(
        efficiencies[0], sequence_one)
print "Session two sequence (efficiency = {0}):\n{1}".format(
        efficiencies[next_best], sequence_two)


# In[29]:

# Save optimized sequences for sessions 1 and 2
np.savetxt('sequence_subject{0}_session1.txt'.format(participant),
           sequence_one, fmt='%d', delimiter=',')
np.savetxt('sequence_subject{0}_session2.txt'.format(participant),
           sequence_two, fmt='%d', delimiter=',')

