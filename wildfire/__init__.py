import pdb
from xml.dom.minidom import parse
from base import assemble
import threading
import time

def run_scripts(doc):
    for node in doc.child_nodes:
        if node.__tag__ == u'script':
            node()
        run_scripts(node)

debug_node_list = []

def debug_tree(tag):
    pass

def run(filename,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #create the tree
    tree = parse(filename)
    
    #we need to go through the document and create all of the classes
    doc = assemble(tree)
    
    #run the scripts after the nodes have been assembled
    run_scripts(doc)
    
    pdb.set_trace()
    
    print "Done."
