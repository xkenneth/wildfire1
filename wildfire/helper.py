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

def call_func(node,func):
    """pre order function call."""
    if hasattr(node,func):
            getattr(node,func)()
    
    for sub_node in node.child_nodes:
        call_func(sub_node,func)    
    
    

def is_junk(node):
    if isinstance(node,xml.dom.minidom.Text) or isinstance(node,xml.dom.minidom.Comment):
        return True

def extend(target,source,attributes=True,ignore_duplicates=False):
    for i in range(len(source.childNodes)):
        for j in range(len(target.childNodes)):
            if ignore_duplicates:
                if source.childNodes[i].tagName == target.childNodes[i].tagName:
                    if len(source.childNodes[i].attributes.keys()) == len(target.childNodes[j].attributes.keys()):
                
            target.childNodes.append(source.childNodes[i])

    if attributes:
        for new_attr in source.attributes.keys():
            target.setAttribute(new_attr,source.attributes[new_attr])
