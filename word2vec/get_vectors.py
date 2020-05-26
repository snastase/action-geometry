import gensim

# replace /home/rebecca/Downloads with location of download
# gensim.models.KeyedVectors.load_word2vec_format('/home/rebecca/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
gensim.models.KeyedVectors.load_word2vec_format('.location/GoogleNews-vectors-negative300.bin', binary=True)

model = gensim.models.KeyedVectors.load_word2vec_format('/home/rebecca/Downloads/GoogleNews-vectors-negative300.bin', binary=True)

# output is 300 value array. Replace word. 
model.word_vec('word')

# verbs that you want to get an array for
verbs = ['verb', 'verb']

# create an empty list
vectors = []

# get an an array for a list of verbs
for verb in verbs: 
vectors.append(model.word_vec(verb))

# check shape
np.vstack(vectors).shape

vectors_arr = np.vstack(vectors)

# distances will give (n*(n-1))/2 values
distances = pdlist(vectors_arr, 'cosine')

# output of squareform is distance array
squareform(distances)

plt.matshow(squareform(distances)); plt.show()

# make a pretty array
sns.heatmap(squareform(distances), square=True, cmap='RdYlBu_r', xticklabels=verbs, yticklabels=verbs)
plt.show

------------
Remember to: 
from scipy.spatial.distance import pdist
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt; import seaborn as sns

