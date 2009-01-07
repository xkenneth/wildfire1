#import sys
#import os

from base import assemble
from elementtree.ElementTree import fromstring
import elementtree.ElementTree as et

from basetags import Library,Import,Handler,Attribute,Class,Script,Replicate,Event,Method
from basetags import node


from helper import call_handlers

tags = {'library':Library,
        'import':Import,
        'handler':Handler,
        'attribute':Attribute,
        'class':Class,
        'script':Script,
        'replicate':Replicate,
        'event':Event,
        'method':Method,
        'node':node}

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
    #gui_libs = ['wtk']
    
    #try to load each one
    #for lib in gui_libs:
    #    Library(doc,module=lib)

    #print "DONE IMPORTING BASE LIBRARIES"

    #get the dom
    dom = et.parse(file).getroot()

    #assemble the child nodes
    children = []
    for child in dom.getchildren():
        children.append(doc.create(child))

    doc.child_nodes = children
        
    call_handlers(doc)
    
