#!/usr/bin/env python

# We use the sequence generator from Geoffrey Aguirre's lab (https://cfn.upenn.edu/aguirre/wiki/public:web-based_sequence_evaluator) to generate the Type 1 Index 1 sequence of stimuli. We have 20 stimulus categories plus a null fixation trial and a catch trial (semantic question), totaling 22 trial categories.

import numpy as np
import itertools
from copy import deepcopy
from scipy.spatial.distance import squareform
from evalseqshard import EvaluateSeqshard, vec2sim
import matplotlib.pyplot as plt
from mvpa2.base.hdf5 import h5save

# Participant number for random seed
participant = 1

# Create dictionary of parameters for EvaluateSeqshard function
parameters = {'N': 20,
              'perms': 1000,
              'TrialDuration': 5,
              'BlankLength': 1,
              'doubleblanks': False,
              'target': 19,
              'numSeqs': 1000}

# Simple similarity matrix separating the 20 categories
category_rdm = np.array([[0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1.],
                         [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0.]])


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

    # Sort efficiencies
    efficiencies = results['bestEs'][0, sort_idx].T

    # Sort sequences
    sequences = results['BestSeqs'][:, sort_idx].T
    assert len(sequences[0]) == int(parameters['N'])**2 + 1

    # Each sequence is $20^2 + 1 = 400$ trials long. We use two sequences ending with the same trial number per participant.

    # Save efficiencies and sequences
    #np.savetxt('sequences_{0}.txt'.format(participant),
    #           sequences, fmt='%d', delimiter=',')
    #np.savetxt('efficiencies_{0}.txt'.format(participant),
    #           efficiencies)

    # Find next best sequence with same starting trial
    # And make sure sequence doesn't have 19, i.e., the question, in trial 1
    for i, sequence in enumerate(sequences):
    
        first_trials = [run[-3] for run in np.split(sequence[1:], 4)]
        print(first_trials)
        if 19. in first_trials:
            print("First trial was question for sequence {0}, "
                      "skipping to next".format(i))
            continue
        else:
            break
    sequence_one = sequence
    sequence_one_id = deepcopy(i)
    print("Found good sequence (number {0})".format(i))
 
    matching_seq_ids = list(np.where(sequences[:, 0] == sequence[0])[0][1:])
    matching_sequences = sequences[matching_seq_ids]
    matching_seq_n = len(matching_seq_ids)

    for i, sequence in enumerate(matching_sequences):
        
        first_trials = [run[-3] for run in np.split(sequence[1:], 4)]
        print(first_trials)
        if 21. in first_trials:
            print("First trial was question for matching sequence {0}, "
                      "skipping to next".format(matching_seq_ids[i]))
            if i + 1 == matching_seq_n:
                raise Exception, "Ran out of matching sequences for participant {0}!!!".format(participant)
            else:
                continue
        else:
            break
    sequence_two = sequence
    sequence_two_id = matching_seq_ids[i]
    print("Found good matching sequence (number {0})".format(matching_seq_ids[i]))

    assert sequence_one[0] == sequence_two[0]
    assert not np.array_equal(sequence_one, sequence_two)

    # Print sequences
    print("Session one sequence (efficiency = {0}):\n{1}".format(
            efficiencies[sequence_one_id], sequence_one))
    print("Session two sequence (efficiency = {0}):\n{1}".format(
            efficiencies[sequence_two_id], sequence_two))

    # Save optimized sequences for sessions 1 and 2
    np.savetxt('sequence_subject{0}_session1.txt'.format(participant),
               sequence_one, fmt='%d', delimiter=',')
    np.savetxt('sequence_subject{0}_session2.txt'.format(participant),
               sequence_two, fmt='%d', delimiter=',')

# Check that all participants have different sequences
all_seqs = []
for participant in range(1, 31):
    for session in [1, 2]:
        with open('sequence_subject{0}_session{1}.txt'.format(participant, session)) as f:
            # Drop first item, we'll append it back on
            all_seqs.append([int(line) for line in f.readlines()][1:])
for a, b in itertools.combinations(all_seqs, 2):                                                                                              
        assert not np.array_equal(a, b)

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
    assert sequence.shape == (8, 103)

    h5save('sequence_final_{0}.hdf5'.format(participant), sequence)
