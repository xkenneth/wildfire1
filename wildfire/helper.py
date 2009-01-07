import re

from elementtree.ElementTree import Element, fromstring, tostring

import os

space_re = re.compile('\s*')
tab_re = re.compile('t*')
constraint_re = re.compile('\${.*}')

def clone(element):
    return fromstring(tostring(element))

def call_handlers(node):
    """After a top-level node has finished construction, we need to call all of the handlers in the proper order."""
    do(node,'construct')
    do(node,'init')
    do_post(node,'script')
    do_post(node,'late')

def find_lib(paths,module):
    for path in paths:
        #if path/module is a dir
        if os.path.isdir(os.path.join(path,module)):
            return os.path.join(path,module,'__init__.wfx')
        # if path/module.wfx is a file
        if os.path.isfile(os.path.join(path,module+'.wfx')):
            return os.path.join(path,module+'.wfx')

def stuff_dict(target_dict,source_dict):
    """Take the contents of the source_dict and stuff it into the target_dict."""
    for k in source_dict.keys():
        target_dict[k] = source_dict[k]
    return target_dict

def correct_indentation(script):
    #make sure that it has any newlines in the first place..
    if script.find('\n') == -1:
        return script
    
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


def do(node,attr):
    node[attr] = True

    for sub_node in node.child_nodes:
        do(sub_node,attr)

def do_post(node,attr):

    for sub_node in node.child_nodes:
        do_post(sub_node,attr)

    node[attr] = True

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
        return True
    else:
        return False
                
if __name__ == '__main__':
    import unittest

    #from xml.dom.minidom import parseString
    
    class HelperTests(unittest.TestCase):
        def setUp(self):
            
            from_string('<temp/>')
            
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

    class CorrectIndentation(unittest.TestCase):
        def test_1(self):
            self.failUnlessEqual(correct_indentation('test1.value + 1'),'test1.value + 1')
        def test_2(self):
            self.failUnlessEqual(correct_indentation('\tdef a():\n\t\tpass'),'def a():\n\tpass\n')

    unittest.main()
