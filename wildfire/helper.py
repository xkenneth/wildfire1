import re
import xml.dom.minidom
import pdb

space_re = re.compile('\s*')
tab_re = re.compile('t*')
constraint_re = re.compile('\${.*}')


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
        try:
            #try to iterate over a list of functions
            #call the list backwards
            for i in range(len(getattr(node,func))):
                getattr(node,func)[-(i+1)]()

        except TypeError:
            #else try to call a singular function
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
                    print "!",node
                    if hasattr(node,func):
                        call_list(node,func)
        
    #we need to return the collection so the function will work recursively
    return collection

def is_junk(node):
    if isinstance(node,xml.dom.minidom.Text) or isinstance(node,xml.dom.minidom.Comment):
        return True

def extend(target,source,attributes=True,ignore_duplicates=False):

    #create copies of the nodes
    target = target.cloneNode(target)
    source = source.cloneNode(source)

    
    #for all the child nodes in the source, append them to the target
    for i in range(len(source.childNodes)):
        target.childNodes.append(source.childNodes[i])
    
    #if we want the attributes
    if attributes:
        #for all of the attributes in the source
        for new_attr in source.attributes.keys():
            #if the target doesn't already have said attribute
            if not target.hasAttribute(new_attr):
                #add them to the target
                target.setAttribute(new_attr,source.attributes[new_attr].value)
                
    return target
                
if __name__ == '__main__':
    import unittest

    from xml.dom.minidom import parseString
    
    class HelperTests(unittest.TestCase):
        def setUp(self):
            doc1 = parseString(u'<temp/>'.encode('UTF-8'))
            node1 = doc1.childNodes[0]
            
            s1 = doc1.createElementNS(None,u'class')
            s1.setAttribute('name','test')
            node1.appendChild(s1)

            s2 = doc1.createElementNS(None,u'handler')
            s2.appendChild(doc1.createTextNode(u"print 'Hi!'"))
            s2.setAttribute('on','init')
            s1.appendChild(s2)

            self.node1 = s1
            
            doc2 = parseString(u'<class/>'.encode('UTF-8'))
            node2 = doc2.childNodes[0]
            node2.setAttribute('name','test2')
            node2.setAttribute('extends','test')

            s3 = doc1.createElementNS(None,u'handler')
            s3.appendChild(doc1.createTextNode(u"print 'Hi2!'"))
            s3.setAttribute('on','init')
            node2.appendChild(s3)
            
            self.node2 = node2
            
        def testExtend(self):
            #print self.node1.toprettyxml()
            new_node1 = self.node1.cloneNode(self.node1)
            #print self.node2.toprettyxml()
            new_node2 = self.node2.cloneNode(self.node2)
            
            extend(new_node1,new_node2)
            
            #print new_node1.toprettyxml()

            #print self.node1.toprettyxml()
            #print self.node2.toprettyxml()

            self.failIfEqual(self.node1,new_node1)

    unittest.main()
