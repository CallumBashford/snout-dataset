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
count = defaultdict(int)

weighted = defaultdict(lambda: defaultdict(int))

for path in glob.glob('{}/**.json'.format('intents')):
    j = json.load(open(path))
    for k, v in j.items():
        for pattern in v:
            pattern = labelmap(pattern)
            if pattern is not None:
                intents[pattern][k]+=1
            count[k]+=1

for _k, _v in intents.items():
    for k, v in _v.items():
        weighted[_k][k] = v / count[k] * 100

json.dump(intents, open('data/intents.json', 'w'))
json.dump(count, open('data/count.json', 'w'))
json.dump(weighted, open('data/weighted.json', 'w'))
