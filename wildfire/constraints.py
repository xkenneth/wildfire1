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
