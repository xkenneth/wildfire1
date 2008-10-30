#import all of the built in tags
from helper import extend, call_func_inorder, call_func_postorder, traverse_postorder, call_by_level, is_constraint, run_scripts
from constraints import Attr, bind
from tags import tags
import gpath
import pdb

doc = None

def assemble(tree,parent=None,data=None):
    """Properly setup a tree of nodes."""

    global doc, uid

    #wipe out our new_node name
    new_node = None
    
    #construct the node, instantantiate it's class and assign the tag
    new_node = construct_class(tree,parent)
    
    #if we tried to construct a junk node such as text, ignore it
    if new_node is None: return

    #if the toplevel doc is none, then the first node we EVER come across should be it
    if doc is None:
        #we want to ignore the #document tag, because it's dumb
        doc = new_node
        doc.events = []
        doc.import_path = './'
    else:
        #assign the doc for reference
        new_node.doc = doc
        
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
    if new_node is not doc:
        #for all of the class defined attributes
        for attr_key in new_node.__wfattrs__:

            if new_node.tag.get(attr_key):                
                attr_val = None
                try:
                    #try to see if the attribute is a python expression (this takes care of converting to int, etc)
                    attr_val = eval(new_node.tag.get(attr_key))

                except SyntaxError:
                    #if that's the case then we need to setup an attribute binding! (constraint)
                    #regex it
                    constraint = is_constraint(new_node.tag.get(attr_key))
                    #got the constraint 
                    if constraint:
                        #turn it into a name
                        try:
                            #it's either global
                            val = eval(constraint)
                        except NameError:
                            #or local
                            val = eval('parent.%s' % constraint)
                            #or a problem...

                        if isinstance(val,Attr):
                            bind(new_node.__wfattrs__[attr_key], val)
                    
                #if not take it as a string
                if attr_val is None:
                    attr_val = new_node.tag.get(attr_key)
                
                new_node.__wfattrs__[attr_key].set(attr_val)

    #if we're at the top level node we need to call the init, early and late handlers

    #early
    
    #init
    #if this is the top-most node as called by assemble
    if not parent:
        #call the defined constructs, inits, and lates in the proper order
        call_func_inorder(new_node,'construct')
        call_func_postorder(new_node,'init')
        #call_func_postorder(new_node,'late')
        #run the script tags
        run_scripts(new_node)
        call_by_level(new_node,func='late')

    #late

    #at the end, return the document
    return new_node


    
def construct_class(node,parent):
    """Create a node from the xml tag."""
    
    #for all of the available tag_names
    for tag in tags:
        #find the tag to create
        if tag.__tag__ == node.tag:
            #create an instance
            new_node = tag(parent,doc)

            #add new tags that have been added
            if hasattr(new_node,'tag'):
                node = extend(node,new_node.tag)
            new_node.tag = node
            
            #add new attributes
            
            return new_node

    #if you reach this point, you've gone to far
    raise TypeError('Tag ( %s ) not found!' % node.tag)
