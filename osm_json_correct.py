# Import python libraries
import re
import json
import codecs
import numpy as np
import xml.etree.cElementTree as ET

def zip_codes(filename):
    count = 0
    data = set()

    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == "addr:postcode":
                    count += 1
                    data.add( tag.attrib['v'] )
                                     
    return count, data

FILEDIR = "/Users/olgabelitskaya/large-repo/"

FILE = FILEDIR + "dubai_abu-dhabi.osm"

JSON_FILE = FILEDIR + "dubai_abu-dhabi.osm.json"

z = zip_codes(FILE)

znp = np.array(sorted(z[1]))

expected = np.append(znp[3:65], znp[66:84])

unexpected0 = np.append(znp[:3], znp[84:])
unexpected = np.insert(unexpected0, 3, znp[65])

correction = {'0': 'NA', '0000': 'NA', '000000': 'NA', '5280 dubai': '5280', 
           'Muhaisnah 4': 'NA', 'P O BOX 3766': '3766', 'P. O. Box 123234': '123234', 
           'P. O. Box 31166': '31166', 'P.O. Box 4605': '4605', 
           'P.O. Box 5618, Abu Dhabi, U.A.E': '5618', 'P.O. Box 6446': '6446', 
           'P.O. Box 9770': '9770', 'PO Box 114822': '114822', 'PO Box 118737': '118737', 
           'PO Box 43377': '43377', 'PO Box 6770': '6770'}

def update_name(name, correction):    
    if name not in unexpected:
        raise Exception(name)
    else:
        unexpect = name        
    replace = correction[unexpect]    
    if not replace:
        raise Exception(unexpect)
    updated_name = re.sub(unexpect, replace, name)
    return updated_name



