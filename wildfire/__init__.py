import pdb
from xml.dom.minidom import parse
from base import assemble
from helper import call_func
import threading
import time

class Datathread(threading.Thread):
    def run(self):
        self.quit = False
        while(not(self.quit)):
            if self.doc is not None:
                call_func(self.doc,'update')                
            time.sleep(0.1) 
            
def run_scripts(doc):
    for node in doc.child_nodes:
        if node.__tag__ == u'script':
            node()
        run_scripts(node)

def run(filename):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    #create the tree
    tree = parse(filename)

    #we need to go through the document and create all of the classes
    doc = assemble(tree)
    
    #call the init methods
    #call_func(doc,'init')

    #run the scripts after the nodes have been assembled
    run_scripts(doc)

    #call the late methods
    call_func(doc,'late')
    
    pdb.set_trace()

    #create the datathread
    #datathread = Datathread()
    
    
    #datathread.doc = doc
    #datathread.start()
    
    #datathread.quit = True

    #datathread.join()
    
