#import all of the built in tags
from tags import tags

doc = None
uid = 0

def assemble(tree,parent=None):
    global doc, uid
    
    #wipe out our new_node name
    new_node = None
    
    #construct the node
    new_node = construct_class(tree)

    #if the toplevel doc is none, then the first node we come across should be it
    if doc is None:
        doc = new_node
        
    #assign the parent if present
    if parent is not None:
        new_node.parent = parent
    
    #construct all of the children recursively
    children = []
    for child in tree.childNodes:
        children.append(assemble(child,new_node))
        
    #attach the children to the node
    new_node.child_nodes = children

    #at the end, return the document
    return new_node

def construct_class(node):
    """Create a node from the xml tag."""
    
    #for all of the available tag_names
    for tag in tags:
        #find the tag to create
        if tag.__tag__ == node.nodeName:
            #create an instance
            new_node = tag()
            #assign the tag
            if hasattr(new_node,'tag'):
                for child_node in node:
                    new_node.tag.append(child_node)
            else:
                new_node.tag = node
            return new_node

    #if you reach this point, you've gone to far
    raise TypeError('Tag not found!')
    
