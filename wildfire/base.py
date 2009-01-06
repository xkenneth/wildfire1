#import all of the built in tags
from helper import extend, call_func_inorder, call_func_postorder, traverse_postorder, call_by_level, is_constraint, run_scripts
from constraints import setup_constraints
import wildfire
import string
from elementtree.ElementTree import tostring

def call_handlers(node):
    """After a top-level node has finished construction, we need to call all of the handlers in the proper order."""
    call_func_inorder(node,'construct')
    call_func_postorder(node,'init')
    #call_func_postorder(node,'late')
    #run the script tags
    run_scripts(node)
    call_by_level(node,func='late')
    
    
def assemble(tree,parent=None,data=None,debug=False):
    """Properly setup a tree of nodes."""

    #wipe out our new_node name
    new_node = None
    
    #construct the node, instantantiate it's class and assign the tag
    new_node = construct_class(tree,parent)
    
    #if we tried to construct a junk node such as text, ignore it
    if new_node is None: return
    
    #print "Constructing node: ",new_node, "\t\t","p:",parent

    #if the toplevel doc is none, then the first node we EVER come across should be it

    #assign the data
    if data is not None:
        new_node.data = data


    #if we've got a handler we need to attach it to the parent
    if new_node.__tag__ == u'replicate':
        #if it's a replicate node, let's assemble it's child nodes
        children = []
        for child,data in new_node.data_nodes:
            new_child = assemble(child,new_node,data)
            if new_child is not None:
                children.append(new_child)
        new_node.child_nodes = children
        #if it's a replicate tag we also need to stop here
        return new_node

    
    #if we're at the top level node we need to call the init, early and late handlers

    #early
    
    #init
    #if this is the top-most node as called by assemble
    if not parent:
        print "Root, calling late."
        #call the defined constructs, inits, and lates in the proper order
        call_handlers(new_node)

    #late

    return new_node


    
def construct_class(node,parent):
    """Create a node from the xml tag."""
    
    #for all of the available tag_names
    for tag in wildfire.tags:
        #find the tag to create
        if tag.__tag__ == node.tag:
            
            #add new tags that have been added
            if hasattr(tag,'tag'):
                node = extend(node,tag.tag)

            #create an instance
            new_node = tag(parent,node)
            
            #add new attributes
            return new_node

        
    #if you reach this point, you've gone to far
    raise TypeError('Tag ( %s ) not found!' % node.tag)
