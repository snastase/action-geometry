#!/usr/bin/env python

# We use the sequence generator from Geoffrey Aguirre's lab (https://cfn.upenn.edu/aguirre/wiki/public:web-based_sequence_evaluator) to generate the Type 1 Index 1 sequence of stimuli. We have 20 stimulus categories plus a null fixation trial and a catch trial (semantic question), totaling 22 trial categories.

import numpy as np
from scipy.spatial.distance import squareform
from evalseqshard import EvaluateSeqshard, vec2sim
import matplotlib.pyplot as plt
from mvpa2.base.hdf5 import h5save

# Participant number for random seed
participant = 1

# Create dictionary of parameters for EvaluateSeqshard function
parameters = {'N': 22,
              'perms': 1000,
              'TrialDuration': 5,
              'BlankLength': 1,
              'doubleblanks': False,
              'target': 21,
              'numSeqs': 100}

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


# Plot RDM
#get_ipython().magic(u'matplotlib inline')
#plt.matshow(category_rdm); plt.show()

# Reformat single RDM for EvaluateSeqshard function
rdms = category_rdm[:, :, None]

# Create sequences for 30 participant indices
for participant in range(1, 31):

    # Set seed to get same sequence across runs
    np.random.seed(participant)
    results = EvaluateSeqshard(parameters, rdms)

    # View condition labels
    # 0 = fixation trial, 21 = catch trial
    print(np.unique(results['BestSeqs'][:, 0]))

    # Sort according to the efficiency
    sort_idx = np.argsort(results['bestEs'][0, :])[::-1]

    # Sort efficiencies and print first few
    efficiencies = results['bestEs'][0, sort_idx].T
    print(efficiencies[:10])

    # Sort sequences and print most efficient
    sequences = results['BestSeqs'][:, sort_idx].T
    assert len(sequences[0]) == int(parameters['N'])**2 + 1
    print(sequences[0].shape, sequences[0])

    # Each sequence is $22^2 + 1 = 485$ trials long. We use two sequences ending with the same trial number per participant.

    # Save efficiencies and sequences
    #np.savetxt('sequences_{0}.txt'.format(participant),
    #           sequences, fmt='%d', delimiter=',')
    #np.savetxt('efficiencies_{0}.txt'.format(participant),
    #           efficiencies)

    # Find next best sequence with same starting trial
    sequence_one = sequences[0]
    next_best = np.where(sequences[:, 0] == sequence_one[0])[0][1]
    sequence_two = sequences[next_best]
    assert not np.array_equal(sequence_one, sequence_two)

    # Print sequences
    print("Session one sequence (efficiency = {0}):\n{1}".format(
            efficiencies[0], sequence_one))
    print("Session two sequence (efficiency = {0}):\n{1}".format(
            efficiencies[next_best], sequence_two))

    # Save optimized sequences for sessions 1 and 2
    np.savetxt('sequence_subject{0}_session1.txt'.format(participant),
               sequence_one, fmt='%d', delimiter=',')
    np.savetxt('sequence_subject{0}_session2.txt'.format(participant),
               sequence_two, fmt='%d', delimiter=',')

# Compile sequence
for participant in range(1, 31):
    session_seqs = []
    for session in [1, 2]:
        with open('sequence_subject{0}_session{1}.txt'.format(participant, session)) as f:
            # Drop first item, we'll append it back on
            seq = [int(line) for line in f.readlines()][1:]

        run_seqs = np.split(np.array(seq), 4)

        extended = []
        extended.append(np.append(run_seqs[-1][-3:], run_seqs[0]))
        for i in range(1, len(run_seqs)):
            extended.append(np.append(run_seqs[i - 1][-3:], run_seqs[i]))

        session_seqs.append(np.array(extended))
    sequence = np.vstack(session_seqs)
    assert sequence.shape == (8, 124)

    h5save('sequence_final_{0}.hdf5'.format(participant), sequence)
