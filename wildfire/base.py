#import all of the built in tags
import pdb
from helper import is_junk, extend, call_func
from tags import tags

doc = None
uid = 0

def assemble(tree,parent=None,data=None):
    """Properly setup a tree of nodes."""

    global doc, uid
    
    #wipe out our new_node name
    new_node = None
    
    #construct the node, instantantiate it's class and assign the tag
    new_node = construct_class(tree)
    
    
    if new_node is None:
        return
    
    #if the toplevel doc is none, then the first node we come across should be it
    if doc is None:
        doc = new_node
    else:
        new_node.doc = doc
        
    #assign the parent if present
    if parent is not None:
        new_node.parent = parent
        
    #assign the data
    if data is not None:
        new_node.data = data

    # call the native construct
    if hasattr(new_node,'_construct'):
        new_node._construct()

    #if we've got a handler we need to attach it to the parent
    if new_node.__tag__ == u'handler':
        #get the handler name
        handler_name = new_node.tag.attributes['on'].childNodes[0].wholeText
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
            setattr(doc,str(new_node.tag.attributes[u'id'].value.value),new_node)
            
    if new_node.tag.attributes:
        if new_node.tag.hasAttribute(u'local'):
            setattr(parent,str(new_node.tag.attributes[u'local'].value.value),new_node)

    # if it's a dataset we need to stop here
    if new_node.__tag__ == u'dataset':
        return    

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
        for attr_key in new_node.__wfattrs__:
            if new_node.tag.hasAttribute(attr_key):
                try:
                    attr_val = eval(new_node.tag.attributes[attr_key].value.value)
                except SyntaxError:
                    attr_val = new_node.tag.attributes[attr_key].value.value
                new_node.__wfattrs__[attr_key].set(attr_val)

    #if we're at the top level node we need to call the init and lates
    

    #early
    
    #init
    #if this is the top-most node as called by assemble
    if not parent:
        #construct it
        print "Later"
        call_func(new_node,'construct',child_first=False)
        
        call_func(new_node,'init')

    #late

    #at the end, return the document
    return new_node


    
def construct_class(node):
    """Create a node from the xml tag."""

    if is_junk(node): return
    
    #for all of the available tag_names
    for tag in tags:
        #find the tag to create
        if tag.__tag__ == node.nodeName:
            #create an instance
            new_node = tag()

            #add new tags that have been added
            if hasattr(new_node,'tag'):
                extend(new_node.tag,node)
            else:
                new_node.tag = node
            
            #add new attributes
                
            return new_node

    #if you reach this point, you've gone to far
    raise TypeError('Tag ( %s ) not found!' % node.nodeName)
