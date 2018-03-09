import argparse
import re
from collections import defaultdict
import json
from justeatpy import JustEat, API_PATH
import uuid

postcode_pattern = re.compile(r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}', re.IGNORECASE)
district_pattern = re.compile(r'[A-Z]{1,2}[0-9]', re.IGNORECASE)

def postcode(s):
    postcodes = s.split(',')
    for i, postcode in enumerate(postcodes):
        if not postcode_pattern.match(postcode) and not district_pattern.match(postcode):
            raise argparse.ArgumentTypeError(postcode)
        postcodes[i] = re.sub(' ', '', postcode)
    return postcodes

parser = argparse.ArgumentParser(description='Scrape intents from JustEat\'s API.')
parser.add_argument('postcode', type=postcode)
# parser.add_argument('-g', '--group', action='group', default=True, help='Group intents (cuisines) that are similar.')

def main(postcode):
    print('Scraping intents for {}'.format(postcode))
    intents = defaultdict(list)
    je = JustEat()
    total = 0
    for res in je.get(API_PATH['restaurants'], postcode=postcode).restaurants:
        print('{}/157 intents found'.format(len(intents)), '--- {} patterns found'.format(total), end='\r')
        for menu in je.get(API_PATH['restaurant_menus'], restaurant_id=res.id).menus:
            for cat in je.get(API_PATH['menu_categories'], menu_id=menu.id).categories:
                for prod in je.get(API_PATH['menu_products'], menu_id=menu.id, category_id=cat.id).products:
                    total+=1
                    intents['+'.join(sorted([cuisine.seo_name.lower().strip() for cuisine in res.cuisine_types]))].append(prod.name.lower().strip())

    if len(intents) > 0:
        json.dump(intents, open('intents/{}.json'.format(uuid.uuid4()), 'w'))
        print('Successfully scraped intents from {}.'.format(postcode))
    else:
        print('Nothing was found for {}. ):'.format(postcode))

if __name__ == '__main__':
    args = parser.parse_args()
    for postcode in args.postcode:
        main(postcode)
