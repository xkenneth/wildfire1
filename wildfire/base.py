#import all of the built in tags
import pdb
from helper import is_junk, extend
from tags import tags

doc = None
uid = 0

def assemble(tree,parent=None,data=None):
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

    #construct it
    if hasattr(new_node,'construct'):
        new_node.construct()

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
        if new_node.tag.hasAttribute(u'name'):
            setattr(parent,str(new_node.tag.attributes[u'name'].value),new_node)

    # if it's a dataset we need to stop here
    if new_node.__tag__ == u'dataset':
        return

    #if we've got a handler we need to attach it to the parent
    if new_node.__tag__ == u'handler':
        setattr(parent,new_node.tag.attributes['on'].childNodes[0].wholeText,new_node)
    
    

    #construct all of the children recursively
    children = []
    for child in new_node.tag.childNodes:
        new_child = assemble(child,new_node)
        if new_child is not None:
            children.append(new_child)

    #init
    #print "Calling init",parent
    #if hasattr(new_node,'_init'): new_node._init()
        
    #attach the children to the node
    new_node.child_nodes = children
    
    #early

    
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
