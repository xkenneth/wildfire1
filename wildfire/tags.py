import pdb
from copy import deepcopy
from helper import correct_indentation, is_junk, extend
import new
import os
from xml.dom.minidom import parse

class node:
    #a list to hold the name of the runtime defined attributes
    __wfattrs__ = {}
    def __repr__(self):
        return "<"+self.__tag__+">"

    def __setattr__(self,name,value):
        try:
            #see if it's a wf specific attribute
            self.__wfattrs__[name].set(value)
        except KeyError:
            #if not set it in the normal method
            self.__dict__[name] = value
    
    def __getattr__(self,name):
        #dangerous overring this i imagine
        #so we look through my custom attributes
        try:
            return self.__wfattrs__[name].get()
        except KeyError:
            #and raise a similar error if we can't find them!!!!!
            raise AttributeError('%s does not exist as a standard or WF attribute' % name)

class Document(node):
    __tag__ = u'#document'

class Library(node):
    __tag__ = u'library'

    def _construct(self):

        #get the module name
        p = self.tag.attributes['library'].nodeValue
        
        #turn it into a path
        p = p.replace('.','/')
        
        #add the file extension
        p = p + '.wfx'
        
        #make sure it's good
        if not os.path.isfile(p):
            raise IOError('%s is not a file!' % p)
        

        #parse it
        library_dom = parse(p)

        #get the child nodes
        library = library_dom.childNodes[0]

        #create the tags

        #wow this is funky....?
        for i in range(len(library.childNodes)):
            self.tag.childNodes.append(library.childNodes[i])

class Import(node):
    __tag__ = u'import'
    def _construct(self):
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

class Attr(object):
    """Class for handling the getting and setting of an attribute."""
    def __init__(self):
        self.value = None

    def set(self,value):
        self.value = value

    def get(self):
        return self.value

class Attribute(node):
    """The actual attribute tag."""

    __tag__ = u'attribute'
    

    def _construct(self):
        #get the attribute
        attr_name = self.tag.attributes['name'].nodeValue
        #self.parent.__attrs__.append(attr_name)
        self.parent.__wfattrs__[attr_name] = Attr()
        #setattr(self.parent,attr_name,property(new_attr.default_set,new_attr.default_get))
        
        #if it's a constraint

        #not sure what the hell this is doing

        #attempt to eval
        #try:
        #    data = eval(self.parent.tag.attributes[attr_name].value.value)
        #except Exception, e:
        #    print e
        #    data = self.parent.tag.attributes[attr_name].value.value
            
        #if self.parent.tag.hasAttribute(attr_name):
        #    setattr(self.parent,attr_name,data)

class Dataset(node):
    __tag__ = u'dataset'
    def _construct(self):
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
    
    def _construct(self):
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
    #def _construct(self):
        #this should probably use an intelligent search function
    #    exec correct_indentation(self.tag.childNodes[0].wholeText)

class Replicate(node):
    __tag__ = u'replicate'
    
    def _construct(self):
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
    
