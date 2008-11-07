from helper import operators
import keyword

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

def constrain(target_node,target_attr,source_node,source_attr):
    """Constraint target_node.target_attr to source_node.source_attr."""
    
    #see if we've already got a list of nodes that the attribute is tied to
    try:
        target_node.__constrained_to__[target_attr]
    except KeyError:
        target_node.__constrained_to__[target_attr] = []

    #target_node.target_attr is now noted as being constrained to source_node.source_attr
    target_node.__constrained_to__[target_attr].append([source_node,source_attr])
    
    #now let's let source_node know that target_node is constrained to it

    try:
        source_node.__constraints__[source_attr]
    except KeyError:
        source_node.__constraints__[source_attr] = {}

    #source_node.source_attr now knows that target_node.target_attr is constrained to it
    source_node.__constraints__[source_attr][target_node.uid] = [target_node,target_attr]

def unconstrain(tag_node,attr_name):
    for cnode,cattr in tag_node.__constrained_to__[attr_name]:
        cnode.__constraints__[cattr].pop(tag_node.uid)

    tag_node.__constrained_to__[attr_name] = {}
    
    
def setup_constraints(tag_node,tag_attr,cstring,local_vars):
    
    cstring = cstring[2:-1]
    
    constrained = False

    new_locals = {'cstring':cstring}

    for oper in cstring.split(' '):
        if oper.strip() != '':
            if not oper.lower() in operators and not keyword.iskeyword(oper.lower()):
                oper_s = oper.split('.')
                if len(oper_s) == 2:
                    if oper_s[0] in local_vars:
                        new_locals[oper_s[0]] = local_vars[oper_s[0]]
                        constrained = True
                        var = local_vars[oper_s[0]]
                        constrain(tag_node,tag_attr,var,oper_s[1])
    
    if constrained:
        t = lambda: eval(cstring,new_locals)
        tag_node._constraint[tag_attr] = t
        tag_node.notify(tag_attr)

    
