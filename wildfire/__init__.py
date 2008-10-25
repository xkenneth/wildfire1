#from xml.dom.minidom import parse
from base import assemble
#import threading
#import time
import pdb

def run_scripts(doc):
    for node in doc.child_nodes:
        if node.__tag__ == u'script':
            node()
        run_scripts(node)

debug_node_list = []

def debug_tree(tag):
    pass

def run(dom,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #create the tree
    #tree = parse(filename)
    #we need to go through the document and create all of the classes 
    #we use the first child cause we don't want to deal with the #document tag
    doc = assemble(dom.childNodes[0])
    pdb.set_trace()
    
    #run the scripts after the nodes have been assembled
    #run_scripts(doc)

