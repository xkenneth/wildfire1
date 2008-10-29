from base import assemble
from gxml import gxml

def run_scripts(doc):
    for node in doc.child_nodes:
        if node.__tag__ == u'script':
            node()
        run_scripts(node)

def run(file,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #we use the first child cause we don't want to deal with the #document tag
    dom = gxml()
    
    dom.parse(file)

    doc = assemble(dom)

    import pdb
    pdb.set_trace()
    
    #run the scripts after the nodes have been assembled
    #run_scripts(doc)

