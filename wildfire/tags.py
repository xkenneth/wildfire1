import pdb
from copy import deepcopy
from helper import correct_indentation, is_junk, extend
import new
import os
from xml.dom.minidom import parse

class node:
    def __repr__(self):
        return "<"+self.__tag__+">"

class Document(node):
    __tag__ = u'#document'

class Library(node):
    __tag__ = u'library'
    def construct(self):

        p = self.tag.attributes['library'].nodeValue
        p.replace('.','/')
        p = p + '.wfx'
        
        if not os.path.isfile(p):
            raise IOError('%s is not a file!' % p)
        

        library_dom = parse()
        library = library_dom.childNodes[0]

        #wow this is funky....?
        for i in range(len(library.childNodes)):
            self.tag.childNodes.append(library.childNodes[i])

class Import(node):
    __tag__ = u'import'
    def construct(self):
        import tags
        tags.__dict__[self.tag.attributes['module'].nodeValue] = __import__(self.tag.attributes['module'].nodeValue)

class Wfx(node):
    __tag__ = u'wfx'

class View(node):
    __tag__ = u'view'

class Handler(node):
    __tag__ = u'handler'
    def __call__(self,event=None):
        exec correct_indentation(self.tag.childNodes[0].wholeText)

class Attribute(node):
    __tag__ = u'attribute'
    def construct(self):
        attr_name = self.tag.attributes['name'].nodeValue
        #attempt to eval
        try:
            data = eval(self.parent.tag.attributes[attr_name].value.value)
        except Exception, e:
            print e
            data = self.parent.tag.attributes[attr_name].value.value
            
        if self.parent.tag.hasAttribute(attr_name):
            setattr(self.parent,attr_name,data)

class Dataset(node):
    __tag__ = u'dataset'
    def construct(self):
        self.data = None

        try:
            self.data = eval(self.tag.child_nodes[0].wholeText)
        except Exception, e:
            print e

        if self.data is None:
            for t in self.tag.childNodes:
                if not is_junk(t):
                    self.data = t
            
    
        
class Class(node):
    __tag__ = u'class'
    
    def construct(self):
        parent_tag = None
        
        #if it's extending something other than view
        if self.tag.hasAttribute('extends'):
            #get what it's looking for
            search_tag = self.tag.attributes['extends'].nodeValue
            #for all the tags
            for tag in tags:
                #find a match
                if search_tag == tag.__tag__:
                    parent_tag = tag
                    #take all of the nodes from the tag we're extending
                    extend(self.tag,parent_tag.tag,attributes=False)
                    #remove the extend tag so we don't recurse?
                    self.tag.removeAttribute('extends')
                    #hold onto to the combined tag
                    parent_tag.tag = self.tag
        else:
            #if we're just extending view
            parent_tag = View
        
            
        #create a copy of the class
        new_class = new.classobj(str(self.tag.attributes['name'].nodeValue),parent_tag.__bases__, parent_tag.__dict__.copy())

        #assign it's new __tag__
        new_class.__tag__ = self.tag.attributes['name'].nodeValue
        
        #attach the DOM tag
        new_class.tag = self.tag
        
        #replace it if necessary
        for i in range(len(tags)):
            if tags[i].__tag__ == new_class.__tag__:
                tags[i] = new_class
                return

        #else just add it to our list of tags
        tags.append(new_class)
        
class Script(Handler):
    __tag__ = u'script'
    #def construct(self):
        #this should probably use an intelligent search function
    #    exec correct_indentation(self.tag.childNodes[0].wholeText)

class Replicate(node):
    __tag__ = u'replicate'
    
    def construct(self):
        self.data_nodes = []
        self.data = eval(self.tag.attributes['over'].nodeValue)
        for data in self.data:
            if not is_junk(data):
            #self.data_nodes.append([self.tag,data])
                for child_node in self.tag.childNodes:
                    if not is_junk(child_node):
                        self.data_nodes.append([child_node,data])
                    #new_node = assemble(child_node,self,data=data)

    def update(self):
        new_data = eval(self.tag.attributes['over'].nodeValue)
        if self.data != new_data:
            print self.data,new_data
            print "Data Changed!"

class Event(node):
    __tag__ = u'event'
                    

tags = [Document,Library,Import,Wfx,View,Handler,Attribute,Dataset,Class,Script,Replicate,Event]
    
