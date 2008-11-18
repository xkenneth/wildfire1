from base import assemble
from gxml import gxml
from tags import Library

def run(file,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #we use the first child cause we don't want to deal with the #document tag
    
    
    #try to find the default GUI libraries
    
    guis = ['wxw','wtk']
    
    for gui in guis:
        try:
            library_dom = gxml()
            library_dom.from_string("<wfx><library library='%s'/></wfx>" % gui)
            ldom = assemble(library_dom)
            print "Using %s" % gui
            break
        except IOError:
            pass

    dom = gxml()

    dom.parse(file)
    
    doc = assemble(dom)
    
