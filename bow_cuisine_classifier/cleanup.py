import argparse
import re
from functools import partial
import glob
import json
from collections import defaultdict
from difflib import SequenceMatcher

import nltk
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')

stemmer = LancasterStemmer()
stop_words = set(stopwords.words('english'))

counter = defaultdict(int)
label_map = []
patterns = []
similarity_keep = []

def clean(sentence, ignore_words=set(stopwords.words('english'))):
    return [stemmer.stem(w.lower()) for w in word_tokenize(sentence) if w not in ignore_words]

def load_word_counts(path):
    j = json.load(open(path))
    for k, v in j.items():
        for pattern in v:
            counter[pattern]+=1

def low(pattern, threshold):
    if counter[pattern] > threshold:
        return pattern
    else:
        return None

def similarity(pattern, threshold):
    if pattern in similarity_keep or pattern not in patterns:
        return pattern
    for p in patterns:
        if(p != pattern):
            m = SequenceMatcher(None, pattern, p)
            if m.ratio() >= threshold:
                # print('{} removed due to similarity to {}'.format(pattern, p))
                similarity_keep.append(p)
                return p
    return pattern

def labelmap(pattern):
    for l in label_map:
        if l in pattern:
            return pattern
    return None

regex_filters = {
    # quantity, sizes
    'labelmap': labelmap,
    'useless': partial(re.sub, r'(\(.+\))|\d+(\s?)(x|"|(\w)?l)|\'', ''),
    'ampersand': partial(re.sub, r'&', 'and'),
    'nonalpha': partial(re.sub, r'[^a-zA-Z0-9&]', ' '),
    'whitespace+': partial(re.sub, r'\s+', ' '),  # concat multiple whitespaces
    'low': low,
    'similarity': similarity
}

def filter_order(_filter):
    return {
        regex_filters['labelmap']: 0
    }.get(_filter, 1)

parser = argparse.ArgumentParser(
    description='Remove unnecessary characters/strings from patterns and merge them into a single document.')
parser.add_argument('directory', nargs='?', type=str, default='intents')
parser.add_argument('-f', '--filter', type=str,
                    default=','.join(regex_filters.keys()))
parser.add_argument('-l', '--low', type=int, default=0)
parser.add_argument('-s', '--similar', type=int, default=.91)
parser.add_argument('-m', '--map', type=str, default='../object_detection/data/label_map.txt')
# parser.add_argument('-b', '--blocked', type=str)


def main(directory, filters, args):
    intents = defaultdict(list)
    if labelmap in filters:
        print('Loading label map (labelmap filter)')
        with open(args.map, 'r') as f:
            labels = [x.strip().replace('_', ' ') for x in f.readlines()]
            for label in labels:
                cleaned = clean(label)
                label_map.extend(cleaned)
        print('Loaded label map (labelmap filter) ({} sub labels)'.format(len(label_map)))
        print(label_map)
    if low in filters or similarity in filters:
        print('Loading word counts (low/similarity filter) --- this may take some time')
        for path in glob.glob('{}/**.json'.format(directory)):
            load_word_counts(path)
        print('Loaded word counts (low/similarity filter) ({} words found)'.format(len(counter)))
    if similarity in filters:
        print('Loading patterns (similarity filter) --- this may take some time')
        for path in glob.glob('{}/**.json'.format(directory)):
            j = json.load(open(path))
            for k, v in j.items():
                for pattern in v:
                    if pattern not in patterns and counter[pattern] > 1:
                        for l in label_map:
                            if l in pattern:
                                patterns.append(pattern)
        print('Loaded patterns (similarity filter) ({} patterns found)'.format(len(patterns)))
    for path in glob.glob('{}/**.json'.format(directory)):
        print(path)
        j = json.load(open(path))
        for k, v in j.items():
            for prod in v:
                if prod in intents[k]:
                    continue
                for f in filters:
                    if prod is None:
                        break
                    if f == low:
                        prod = f(prod, args.low)
                    elif f == similarity:
                        prod = f(prod, args.similar)
                    else:
                        prod = f(prod)
                if prod not in intents[k] and prod is not None:
                    intents[k].append(prod)
    json.dump(intents, open('data/intents.json', 'w'))
    print('Successfully cleaned up intents')


def get_filter(args):
    filters = []
    for key in args.filter.split(','):
        if key not in regex_filters:
            raise KeyError("'{}' is not a valid filter".format(key))
        filters.append(regex_filters[key])
    return filters


if __name__ == '__main__':
    args = parser.parse_args()
    filters = get_filter(args)
    filters.sort(key=filter_order)
    main(args.directory, filters, args)
