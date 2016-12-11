# Import python libraries
import re
import json
import codecs
import xml.etree.cElementTree as ET

# Strings containing lower case chars
lower = re.compile(r'^([a-z]|_)*$')
# Strings with lower case chars and a ':'
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
# Strings with chars that will cause problems as keys
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Setup the set of tags
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

# Mapping the right postcodes
correction = {'0': 'NA', '0000': 'NA', '000000': 'NA', '5280 dubai': '5280', 
           'Muhaisnah 4': 'NA', 'P O BOX 3766': '3766', 'P. O. Box 123234': '123234', 
           'P. O. Box 31166': '31166', 'P.O. Box 4605': '4605', 
           'P.O. Box 5618, Abu Dhabi, U.A.E': '5618', 'P.O. Box 6446': '6446', 
           'P.O. Box 9770': '9770', 'PO Box 114822': '114822', 'PO Box 118737': '118737', 
           'PO Box 43377': '43377', 'PO Box 6770': '6770'}

# Function for update postcodes
def update_name(name, correction):    
    if name not in correction.keys():
        raise Exception(name)
    else:
        unexpect = name        
    replace = correction[unexpect]    
    if not replace:
        raise Exception(unexpect)
    updated_name = re.sub(unexpect, replace, name)
    return updated_name

# Function for creating nodes
def shape_element(element):
# Create the empty dictionary for the data in the osm string
    node = {}
    if element.tag == "node" or element.tag == "way":
        # Create the empty dictionary for the 'address' attributes and the list for the 'nd' attribute
        address = {}
        nd = []
        # Add the type and the id of the element
        node["type"] = element.tag
        node["id"] = element.attrib["id"]
        # Add the tag 'visible'
        if "visible" in element.attrib.keys():
            node["visible"] = element.attrib["visible"]
        # Add the geoposition
        if "lat" in element.attrib.keys():
            node["pos"] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        # Add the set of the attributes
        node["created"] = {"version": element.attrib['version'],
                            "changeset": element.attrib['changeset'],
                            "timestamp": element.attrib['timestamp'],
                            "uid": element.attrib['uid'],
                            "user": element.attrib['user']}
        # Analize the problemchars and add address attributes
        for tag in element.iter("tag"):
            p = problemchars.search(tag.attrib['k'])
            if p:
                print "problemchars: ", p.group()
                continue
            elif tag.attrib['k'][:5] == "addr:":
                if ":" in tag.attrib['k'][5:]:
                    continue
                else:
                    # Correction of postcodes
                    if tag.attrib['k'] == "addr:postcode":
                        if tag.attrib['v'] in correction.keys():
                            address[tag.attrib['k'][5:]] = update_name(tag.attrib['v'], correction)                     
                    else:
                        address[tag.attrib['k'][5:]] = tag.attrib['v']
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        if address != {}:
            node['address'] = address
        # Add the 'node_ref' attribute
        for tag2 in element.iter("nd"):
            nd.append(tag2.attrib['ref'])
        if nd != []:
            node['node_refs'] = nd
        return node
    # Skip elements without the tags 'node' or 'way'
    else:
        return None
    
# Function for creating the .json file
def process_map(file_in, pretty = False):
    # Setup the format for output files
    file_out = "{0}.json".format(file_in)
    # Create the empty data
    data = []
    # Open the osm file and read strings
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            # Apply the created function 'shape_element'
            el = shape_element(element)
            if el:
                data.append(el)
                # Write the element into the json file
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data