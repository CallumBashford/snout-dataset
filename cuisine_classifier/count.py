import json
from collections import defaultdict
import glob

label_map = json.load(open('data/label_map.json', 'r'))

def labelmap(pattern):
    # print(label_map)
    for k, v in label_map.items():
        for l in v:
            if l in pattern:
                return k
    return None

intents = defaultdict(lambda: defaultdict(int))

for path in glob.glob('{}/**.json'.format('intents')):
    j = json.load(open(path))
    for k, v in j.items():
        for pattern in v:
            pattern = labelmap(pattern)
            if pattern is not None:
                intents[pattern][k]+=1

json.dump(intents, open('data/intents.json', 'w'))
