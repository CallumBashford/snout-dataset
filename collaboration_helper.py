import xml.etree.ElementTree
import glob, os

"""
Hacky script that (more like tries) to standardize labelImg output between collaborators.
"""

for path in glob.glob('annotations/**/*.xml'):
    try:
        et = xml.etree.ElementTree.parse(path)
    except Exception as e:
        print('Failed to parse "{}"'.format(path))
        continue
    if et.find('path') is not None:
        et.getroot().remove(et.find('path'))

    if et.find('filename') is not None:
        et.find('filename').text = et.find('filename').text.rsplit('.', 1)[0]
    else:
        print('Cannot process "{}" - Invalid XML'.format(path))
        continue

    if et.find('folder') is not None:
        et.find('folder').text = et.find('folder').text.lower()
        folder = et.find('folder').text
        base = os.path.basename(os.path.dirname(path))
        # Correct file but folder attribute is incorrect
        if(folder != base):
            et.find('folder').text = base.lower()
        # Add file extension to xml
        img = glob.glob('images/{}/{}.*'.format(base, et.find('filename').text))[0]
        if img is None:
            print('Cannot process "{}" - Matching image cannot be found'.format(path))
            continue
        ext = img.split('.')[1]
        new_tag = xml.etree.ElementTree.SubElement(et.getroot(), 'filetype')
        new_tag.text = ext
    et.write(path)



# et = xml.etree.ElementTree.parse('annotations/french_fries/3139.xml')
#
# element = et.find('path')
# if element:
#     et.getroot().remove(element)
#
# et.find('filename').text = 'test'
#
# et.write('annotations/french_fries/3139.xml')
