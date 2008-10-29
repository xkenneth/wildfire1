import re

from gxml import gxml, clone, Element

space_re = re.compile('\s*')
tab_re = re.compile('t*')
constraint_re = re.compile('\${.*}')

uid = 0

def get_uid():
    global uid
    last = uid
    uid += 1
    print last
    return last

def correct_indentation(script):
    #split by line, take the first empty line out
    lines = script.split('\n')
    
    #get rid of the first line if it's empty
    if lines[0] == '':
        lines = lines[1:]
        
    #find out the number of tabs at the front of the line
    num_tabs = len(tab_re.match(lines[0]).group())
    num_spaces = len(space_re.match(lines[0]).group())

    proper_script = ''
    #for each line, remove the number of tabs
    for line in lines:
        proper_script += line[num_tabs+num_spaces:] + '\n'
        
    return proper_script

def call_list(node,func):
    #if we've got the function
    if hasattr(node,func):
        func_list = getattr(node,func)
        if hasattr(func_list,'__iter__'):
            #try to iterate over a list of functions
            #call the list backwards
            func_list.reverse()
            #try to iterate over a list of functions - I HAVE GOOD REASON FOR THIS
            for f in func_list:
                f()
        else:
            #else try to call a singular function
            #print getattr(node,func)
            getattr(node,func)()

def call_func_inorder(node,func):
    call_list(node,func)
    for sub_node in node.child_nodes:
            call_func_inorder(sub_node,func)   
        
        
def call_func_postorder(node,func):
    """pre order function call."""
    
    for sub_node in node.child_nodes:
        call_func_postorder(sub_node,func)

    call_list(node,func)

def traverse_postorder(node):
    for sub_node in node.child_nodes:
        traverse_postorder(sub_node)
    
def call_by_level(node,collection=[],depth=0,func=None,top_down=False):
    """Fire a function by depth of the nodes. All nodes at depth N will be fired before
    nodes at depth N-1"""
    
    try:
        #see if a list of nodes exists at this depth
        collection[depth].append(node)
    except IndexError:
        #if not create the list with the current node in it
        collection.append([node])
        
    #for all of the children
    for child_node in node.child_nodes:
        #do the same thing, noting an increase in depth, make sure the collection gets passed
        collection = call_by_level(child_node,collection=collection,depth=depth+1)

    #now we should have a list containing lists of the nodes at each level
    if func is not None:
        #operating top down
        if top_down:
            for level in collection:
                for node in level:
                    #call said function if it exists
                    if hasattr(node,func):
                        call_list(node,func)
        else:
            #operating bottom up
            for level in range(len(collection)):
                for node in collection[-(level+1)]:
                    if hasattr(node,func):
                        call_list(node,func)
        
    #we need to return the collection so the function will work recursively
    return collection

#def is_junk(node):
#    #if isinstance(node,xml.dom.minidom.Text) or isinstance(node,xml.dom.minidom.Comment):
#    if node.tag == u'#text' or node.tag == u'#comment' or node.tag == u'#cdata-section':
#        return True

def extend(target,source,attributes=True,ignore_duplicates=False):

    #create copies of the nodes
    target = clone(target)
    source = clone(source)

    
    #for all the child nodes in the source, append them to the target
    for i in source:
        target.append(i)
    
    #if we want the attributes
    if attributes:
        #for all of the attributes in the source
        for new_attr in source.keys():
            #if the target doesn't already have said attribute
            if not target.get(new_attr):
                #add them to the target
                target.set(new_attr,source.get(new_attr))
                
    return target

def is_constraint(str):
    match = constraint_re.match(str)
    if match:
        #if we've got a group, slice and return
        return match.group()[2:-1]
                
if __name__ == '__main__':
    import unittest

    #from xml.dom.minidom import parseString
    
    class HelperTests(unittest.TestCase):
        def setUp(self):
            t = gxml()
            t.from_string('<temp/>')
            
            s1 = Element('class')
            s1.set('name','test')
            t.append(s1)

            s2 = Element('handler')
            s2.text = "print 'Hi!'"
            s2.set('on','init')
            s1.append(s2)

            self.node1 = s1
            
            doc2 = Element('class')
            doc2.set('name','test2')
            doc2.set('extends','test')

            s3 = Element('handler')
            s3.text = 'print Hi2!'
            s3.set('on','init')

            doc2.append(s3)
            
            self.node2 = doc2
            
        def testExtend(self):
            #print self.node1.toprettyxml()
            new_node1 = clone(self.node1)
            #print self.node2.toprettyxml()
            new_node2 = clone(self.node2)
            
            extend(new_node1,new_node2)
            
            #print new_node1.toprettyxml()

            #print self.node1.toprettyxml()
            #print self.node2.toprettyxml()

            self.failIfEqual(self.node1,new_node1)

    unittest.main()
