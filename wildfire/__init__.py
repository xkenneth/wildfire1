from base import assemble

def run_scripts(doc):
    for node in doc.child_nodes:
        if node.__tag__ == u'script':
            node()
        run_scripts(node)

def run(dom,debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #we use the first child cause we don't want to deal with the #document tag
    doc = assemble(dom)
    
    #run the scripts after the nodes have been assembled
    #run_scripts(doc)

