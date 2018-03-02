import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET

def xml_to_csv(path):
    xml_list = []
    labels = []
    for xml_file in glob.glob(path + '/**/*.xml', recursive=True):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            if member[0].text not in labels:
                labels.append(member[0].text)
            value = (root.find('folder').text + '/' + root.find('filename').text + '.' + root.find('filetype').text,
                    int(root.find('size')[0].text),
                    int(root.find('size')[1].text),
                    member[0].text,
                    int(member[4][0].text),
                    int(member[4][1].text),
                    int(member[4][2].text),
                    int(member[4][3].text)
                    )
            xml_list.append(value)

    with open('data/label_map.txt', 'w') as lm, open('training/object-detection.pbtxt', 'w') as pb:
        for i, label in enumerate(labels):
            print(label, end='\n', file=lm)

            # Don't hate, we're lazy.
            print('item {', end='\n', file=pb)
            print('  id: {}'.format(i + 1), end='\n', file=pb)
            print("  name: '{}'".format(label), end='\n', file=pb)
            print('}', end='\n\n', file=pb)

    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

def main():
    xml_df = xml_to_csv('annotations')
    xml_df.to_csv('data/food_labels.csv', index=None)
    print('Successfully converted xml to csv.')

if __name__ == '__main__':
    main()
