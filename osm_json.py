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