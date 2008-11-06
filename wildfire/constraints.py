def bind(tag_node,attr_name,setter,setter_context,getter=None,getter_context=None):
    """Bind an attribute to a variable. This is different from a constraint."""

    try:
        #see if a list already exists for the specified attribute
        tag_node.__bindings__[attr_name]
    except KeyError:
        #if not create it
        tag_node.__bindings__[attr_name] = []
        
    #and then append the (lambda) function
    tag_node.__bindings__[attr_name].append([setter,setter_context])
    
    #if we have a getter function
    if getter:
        try:
            tag_node.__getters__[attr_name]
        except: 
            tag_node.__getters__[attr_name] = []
        
        tag_node.__getters__[attr_name].append([getter,getter_context])

def unbind(tag_node,attr_name):
    """Release the binding of an attribute from a variable."""
    tag_node.__bindings__[attr_name] = []
    tag_node.__getters__[attr_name] = []
    
