from pickle import load
from pickle import dump
from numpy.random import rand
from numpy.random import shuffle

# Load a clean dataset
def load_clean_sentences(filename):
	return load(open(filename, 'rb'))

# Save a list of clean sentences to file
def save_clean_data(sentences, filename):
	dump(sentences, open(filename, 'wb'))
	print('Saved: %s' % filename)

# Load dataset
raw_dataset = load_clean_sentences('english-sami.pkl')

print("Dataset size:", len(raw_dataset))
dataset = raw_dataset
# Random shuffle
shuffle(dataset)
# Split into train/test
train, test = dataset[:4000], dataset[4000:]
# Save
save_clean_data(dataset, 'english-sami-both.pkl')
save_clean_data(train, 'english-sami-train.pkl')
save_clean_data(test, 'english-sami-test.pkl')