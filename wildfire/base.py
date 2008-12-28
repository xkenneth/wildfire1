#import all of the built in tags
from helper import extend, call_func_inorder, call_func_postorder, traverse_postorder, call_by_level, is_constraint, run_scripts
from constraints import setup_constraints
import wildfire
import string
from elementtree.ElementTree import tostring

#def wrap_assemble(func):
#    def inner_func(*args,**kwargs):
#        data = func(*args,**kwargs)
#        #print "Ending construction:", data
#        return data
#    return inner_func

def call_handlers(node):
    """After a top-level node has finished construction, we need to call all of the handlers in the proper order."""
    call_func_inorder(node,'construct')
    call_func_postorder(node,'init')
    #call_func_postorder(node,'late')
    #run the script tags
    run_scripts(node)
    call_by_level(node,func='late')
    
    
#@wrap_assemble
def assemble(tree,parent=None,data=None,debug=False):
    """Properly setup a tree of nodes."""

    #wipe out our new_node name
    new_node = None
    
    #construct the node, instantantiate it's class and assign the tag
    new_node = construct_class(tree,parent)
    
    #if we tried to construct a junk node such as text, ignore it
    if new_node is None: return

    
    print "Constructing node: ",new_node, "\t\t","p:",parent

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

    #if the tag class accepts names, ie, classes don't accept names
    if new_node._name:
        #handling names and ids
        if new_node.tag.get('id'):
            #attaching the node to it's parent as the given id
            setattr(doc,str(new_node.tag.get('id')),new_node)
            
        if new_node.tag.get('name'):
            #attaching the node to it's parent as the given name
            setattr(parent,str(new_node.tag.get('name')),new_node)


    #if we don't want to instantiate a node's children, we need to stop now
    if not new_node._instantiate_children:
        return new_node

    #construct all of the children recursively
    children = []
    for child in new_node.tag:
        new_child = assemble(child,new_node)
        if new_child is not None:
            children.append(new_child)

    #attach the children to the node
    new_node.child_nodes = children
    
    
    #handling given attributes - we need to do this after all of the attribute tags have been executed
    if new_node is not new_node.doc:
        #for all of the class defined attributes
        for attr_key in new_node.__wfattrs__:

            if new_node.tag.get(attr_key) is not None:                
                if is_constraint(new_node.tag.get(attr_key)):
                    #constrain it!
                        setup_constraints(new_node,attr_key,new_node.tag.get(attr_key),parent.__dict__)
                else:
                    attr_val = None
                    #try to see if the attribute is a python expression (this takes care of converting to int, etc)
                    #try:
                    #    this = new_node
                    #    attr_val = eval(new_node.tag.get(attr_key))
                    #except Exception, e:
                    #    print e
                        #if not take it as a string
                    attr_val = new_node.tag.get(attr_key)
                
                    #set the value of the attribute
                    setattr(new_node,attr_key,attr_val)

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
