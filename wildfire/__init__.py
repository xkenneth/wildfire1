#import sys
#import os

from base import assemble
from elementtree.ElementTree import fromstring
import elementtree.ElementTree as et

from basetags import Library,Import,Handler,Attribute,Class,Script,Replicate,Method,node


from helper import call_handlers

tags = {'library':Library,
        'import':Import,
        'handler':Handler,
        'attribute':Attribute,
        'class':Class,
        'script':Script,
        'replicate':Replicate,
        'method':Method,
        'node':node}

path = ['.','lib']

#for p in path:
#    sys.path.append(os.path.join(os.getcwd(),p))

def run(file,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #we use the first child cause we don't want to deal with the #document tag
    
    
    #initiate the base document
    doc = node()

    #insert the application node into scope
    basetags.__dict__['application'] = doc
    
    #get the dom
    dom = et.parse(file).getroot()

    #assemble the child nodes
    children = []
    for child in dom.getchildren():
        new_child = doc.create(child)
        if new_child is not None:
            children.append(new_child)

    doc.child_nodes = children
        
    call_handlers(doc)
    
