#import sys
#import os

from base import assemble
from elementtree.ElementTree import fromstring
import elementtree.ElementTree as et

from basetags import Library,Import,Wfx,View,Handler,Attribute,Class,Script,Replicate,Event,Method
from basetags import node

from base import call_handlers

tags = [Library,Import,Wfx,View,Handler,Attribute,Class,Script,Replicate,Event,Method]

path = ['.','lib']

#for p in path:
#    sys.path.append(os.path.join(os.getcwd(),p))

def run(file,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #we use the first child cause we don't want to deal with the #document tag
    
    
    #try to find the default GUI libraries
    
    # guis = ['wxw','wtk']
    
#     for gui in guis:
#         try:
#             print gui
#             library_dom = fromstring("<wfx><library library='%s'/></wfx>" % gui)
            
#             print "dom"
#             ldom = assemble()
#             print "Using %s" % gui
#             break
#         except IOError, e:
#             print e
#             print "error"
#             pass

    #initiate the base document
    doc = node()

    #predefined gui libs
    gui_libs = ['wxw']
    
    #try to load each one
    for lib in gui_libs:
        Library(doc,module=lib)

    print "DONE IMPORTING BASE LIBRARIES"

    #get the dom
    dom = et.parse(file).getroot()

    #assemble the child nodes
    children = []
    for child in dom.getchildren():
        children.append(assemble(child,doc))

    doc.child_nodes = children
        
    call_handlers(doc)
    
