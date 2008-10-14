#import all of the built in tags
import pdb
from copy import copy
from helper import is_junk, extend, call_func_inorder, call_func_postorder, traverse_postorder, call_by_level
from tags import tags
import os
import threading

doc = None
uid = 0

def assemble(tree,parent=None,data=None):
    """Properly setup a tree of nodes."""

    global doc, uid

    #wipe out our new_node name
    new_node = None

    #construct the node, instantantiate it's class and assign the tag
    new_node = construct_class(tree,parent)
    
    #if we tried to construct a junk node such as text, ignore it
    if new_node is None: return

    print new_node

    #if the toplevel doc is none, then the first node we come across should be it
    if doc is None:
        #we want to ignore the #document tag, because it's dumb
        doc = new_node
        doc.events = []
        doc.import_path = os.getcwd()
    else:
        #assign the doc directly
        new_node.doc = doc
        
    #assign a global UID to each node (useful for debug mostly)
    new_node.uid = uid
    uid += 1
        
    #assign the data
    if data is not None:
        new_node.data = data

    # call the native construct
    if hasattr(new_node,'_construct'):
        new_node._construct()

    if new_node.__tag__ == u'library':
        children = []

        for lnode in new_node.library_nodes:
            new_lnode = assemble(lnode,parent=new_node,data=data)
            if new_lnode:
                children.append(new_lnode)

        new_node.child_nodes = children

        setattr(parent,new_node.module,new_node)
        
        return new_node

    #if we've got a handler we need to attach it to the parent
    if new_node.__tag__ == u'handler':
        #get the handler name
        handler_name = new_node.tag.attributes['on'].nodeValue
        #if a list hasn't been setup for this handler
        if not hasattr(parent,handler_name):
            #create it
            setattr(parent,handler_name,[])
        else:
            #if it is there, and it's not a list
            if not isinstance(getattr(parent,handler_name),list):
                #make it into a list with the first item as the old value
                setattr(parent,handler_name,[getattr(parent,handler_name)])
            
        #append the new handler
        getattr(parent,handler_name).append(new_node)


    #if it's a class we need to stop here
    if new_node.__tag__ == u'class':
        return

    
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

    #handling names and ids
    
    if new_node.tag.attributes:
        if new_node.tag.hasAttribute(u'id'):
            setattr(doc,str(new_node.tag.attributes[u'id'].value),new_node)
            
    if new_node.tag.attributes:
        if new_node.tag.hasAttribute(u'local'):
            setattr(parent,str(new_node.tag.attributes[u'local'].value),new_node)

    # if it's a dataset we need to stop here
    if new_node.__tag__ == u'dataset':
        return    

    #CREATING THE CHILDREN

    #construct all of the children recursively
    children = []
    for child in new_node.tag.childNodes:
        new_child = assemble(child,new_node)
        if new_child is not None:
            children.append(new_child)

    #attach the children to the node
    new_node.child_nodes = children
    
    
    
    #handling given attributes - we need to do this after all of the attribute tags have been executed
    if new_node is not doc:
        #for all of the class defined attributes
        for attr_key in new_node.__wfattrs__:

            if new_node.tag.hasAttribute(attr_key):                
                attr_val = None
                try:
                    #try to see if the attribute is a python expression (this takes care of converting to int, etc)
                    attr_val = eval(new_node.tag.attributes[attr_key].value)
                except NameError:
                    pass
                except SyntaxError:
                    pass
                    
                #put some tests in here for checking for constraints

                #if not take it as a string
                if attr_val is None:
                    attr_val = new_node.tag.attributes[attr_key].value
                
                new_node.__wfattrs__[attr_key].set(attr_val)

    #if we're at the top level node we need to call the init and lates
    

    #early
    
    #init
    #if this is the top-most node as called by assemble
    if not parent:
        call_func_inorder(new_node,'construct')
        call_func_postorder(new_node,'init')
        #call_func_postorder(new_node,'late')
        call_by_level(new_node,func='late')

    #late

    #at the end, return the document
    return new_node


    
def construct_class(node,parent):
    """Create a node from the xml tag."""
    
    if is_junk(node): return
    
    #for all of the available tag_names
    for tag in tags:
        #find the tag to create
        if tag.__tag__ == node.nodeName:
            #create an instance
            new_node = tag(parent)

            #add new tags that have been added
            if hasattr(new_node,'tag'):
                node = extend(node,new_node.tag)
            new_node.tag = node
            
            #add new attributes
            
            return new_node

    #if you reach this point, you've gone to far
    raise TypeError('Tag ( %s ) not found!' % node.nodeName)
