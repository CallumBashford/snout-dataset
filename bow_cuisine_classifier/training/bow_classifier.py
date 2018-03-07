import nltk
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

stemmer = LancasterStemmer()
stop_words = set(stopwords.words('english'))

import numpy as np
import tflearn
import tensorflow as tf
from tflearn.data_utils import to_categorical, pad_sequences
import random
import json

with open('../data/intents.json') as f:
    j = json.load(f)

intents = []
for k, v in j.items():
    intents.append({'tag': k, 'patterns': v})

def clean(sentence, ignore_words=set(stopwords.words('english'))):
    return [stemmer.stem(w.lower()) for w in word_tokenize(sentence) if w not in ignore_words]

def bow(sentence, words, show_details=False):
    # tokenize pattern
    sentence_words = clean(sentence)
    print(sentence_words)
    # bag of words
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print('Found in bag: %s' % w)
    return np.array(bag)

words = []
classes = []
documents = []
ignore_words = ['?']

#loop through each sentence in our intents patterns
for intent in intents:
    print(intent['tag'])
    for pattern in intent['patterns']:
        # tokenize each word in the sentence
        w = word_tokenize(pattern)
        # add to our words list
        words.extend(w)
        # add to documents in our corpus (body of text)
        documents.append((w, intent['tag']))
        # add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# stem, lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in stop_words]
# words = [w.lower() for w in words if w not in stop_words]
words = sorted(list(set(words)))

# remove duplicate
classes = sorted(list(set(classes)))

print(len(documents), 'documents')
print(len(classes), 'classes', classes)
print(len(words), 'unique stemmed words', words)

# create our training data
training = []
output = []
# create an empty array for our output
output_empty = [0] * len(classes)

import sys

# training set, bag of words for each sentence
for i, doc in enumerate(documents):
    sys.stdout.write('\r' + str(i) + '/' + str(len(documents)))
    sys.stdout.flush()

    # initialize our bag of words
    bag = []
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    # stem each word
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # create our bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # output is a '0' for each tag and '1' for current tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])


random.shuffle(training)
training = np.array(training)

train_x = list(training[:,0])
train_y = list(training[:,1])

# reset underlying graph
tf.reset_default_graph()

# build nn
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 32)
net = tflearn.fully_connected(net, 32)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_verbose=0, tensorboard_dir='tflearn_logs')
# Start training (apply gradient descent algorithm)
model.fit(train_x, train_y, n_epoch=1000, validation_set=0.1, batch_size=16, show_metric=True)
model.save('model.tflearn')

def classify(sentence, threshold=0):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]
    # filter out predictions below the threshold
    results = [[i, r] for i,r in enumerate(results) if r>threshold]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    return return_list

classify('chicken korma')
