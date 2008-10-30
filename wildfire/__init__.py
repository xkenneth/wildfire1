from base import assemble
from gxml import gxml

def run(file,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #we use the first child cause we don't want to deal with the #document tag
    dom = gxml()
    
    dom.parse(file)

    doc = assemble(dom)
