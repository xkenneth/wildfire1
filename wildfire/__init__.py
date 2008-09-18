import pdb
from xml.dom.minidom import parse
from base import assemble

def run(filename):
    """Parse the XML file, create the environment, and run."""
    
    #create the tree
    tree = parse(filename)

    #we need to handle importing requisite python modules here

    #we need to go through the document and create all of the classes
    doc = assemble(tree)

    pdb.set_trace()

    
