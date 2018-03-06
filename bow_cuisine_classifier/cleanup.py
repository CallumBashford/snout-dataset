import argparse
import re
from functools import partial
import glob
import json
from collections import defaultdict

regex_filters = {
    'useless': partial(re.sub, r'(\(.+\))|\d+(\s?)(x|"|(\w)?l)|\'', ''), # quantity, sizes
    'ampersand': partial(re.sub, r'&', 'and'),
    'nonalpha': partial(re.sub, r'[^a-zA-Z0-9&]', ' '),
    'whitespace+': partial(re.sub, r'\s+', ' ') # concat multiple whitespaces
}

parser = argparse.ArgumentParser(description='Remove unnecessary characters/strings from patterns and merge them into a single document.')
parser.add_argument('directory', nargs='?', type=str, default='intents')
parser.add_argument('-f', '--filter', type=str, default=','.join(regex_filters.keys()))
# parser.add_argument('-b', '--blocked', type=str)

def main(directory, filters):
    intents = defaultdict(list)
    for path in glob.glob('{}/**.json'.format(directory)):
        print(path)
        j = json.load(open(path))
        for k, v in j.items():
            for prod in v:
                for f in filters:
                    prod = f(prod)
                if prod not in intents[k]:
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
    main(args.directory, filters)
