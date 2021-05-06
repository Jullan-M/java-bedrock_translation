import string
import re
from pickle import dump
from unicodedata import normalize
from numpy import array
from utilities import *

# Load language pair
def load_pairs(filename1, filename2):
    loc1 = file2dict(filename1)
    loc2 = file2dict(filename2)
    keys = set(loc1.keys()) & set(loc2.keys())
    pairs = [ [loc1[k].replace("%s", ""), loc2[k]] for k in keys ]
    return pairs

# Clean a list of lines
def clean_pairs(lines):
    cleaned = list()
    # Prepare regex for char filtering
    re_print = re.compile('[^%s]' % re.escape(string.printable + "ášŧŋđžčÁŠŦŊĐŽČ"))
    # Prepare translation table for removing punctuation
    table = str.maketrans('', '', string.punctuation)
    for pair in lines:
        clean_pair = list()
        for line in pair:
            # Tokenize on white space
            line = line.split()
            # Convert to lowercase
            line = [word.lower() for word in line]
            # Remove punctuation from each token
            line = [word.translate(table) for word in line]
            # Remove non-printable chars form each token
            line = [re_print.sub('', w) for w in line]
            # Remove tokens with numbers in them
            line = [word for word in line if word.isalpha()]
            # Store as string
            clean_pair.append(' '.join(line))
        cleaned.append(clean_pair)
    return array(cleaned)

# Save a list of clean sentences to file
def save_clean_data(sentences, filename):
	dump(sentences, open(filename, 'wb'))
	print('Saved: %s' % filename)

# Load and split into english-sami pairs
pairs = load_pairs("Locales/se_no.json", "Locales/en_us.json")
# Clean sentences
clean_pairs = clean_pairs(pairs)
print('Number of clean pairs: %s' % len(clean_pairs))
# Save clean pairs to file
save_clean_data(clean_pairs, 'english-sami.pkl')
# Spot check
for i in range(100):
	print('[%s] => [%s]' % (clean_pairs[i,0], clean_pairs[i,1]))