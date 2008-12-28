from helper import correct_indentation, extend, get_uid, uid, find_lib

from base import assemble

from constraints import bind

from elementtree.ElementTree import parse

import wildfire

import sys

import os

import string

class node:
    """The base class for all other nodes."""
    #by default
    _name = True
    _instantiate_children = True
    
    def get_doc(self):

        #if we don't have a parent, this must be the doc
        if self.parent is None:
            return self

        parent = self.parent

        while(1):
            if parent.parent is None:
                break
            parent = parent.parent
        
        return parent
    
    doc = property(get_doc)

    def __init__(self,parent=None,tag=None,data=None,**kwargs):

        #contains a list of attributes defined by <attribute> tags
        
        if not '__wfattrs__' in self.__dict__:
            self.__dict__['__wfattrs__'] = {}

        #the parent tag of this tag
        self.parent = parent
        
        if self.parent is None:
            #we're the doc! Let's announce it, since it's sort of a big deal
            print "IM THE DOC:",self
            self.events = []

        #the children of this tag
        self.child_nodes = []
        
        #this tags uid
        self.uid = get_uid()

        #data from a replicate
        self.data = data

        #the actual tag (xml) from which this class tag as instantiated from
        self.tag = tag

        #bindings are constraints where we set the value
        self.__bindings__ = {}

        #some attribute values need to be retrieved
        self.__getters__ = {}
        
        #constraints are simply notifactions of an attribute to re-evaluate itself
        self.__constraints__ = {}

        #the nodes.attrs that this node.attr is constrained to
        self.__constrained_to__ = {}

        #the function that gets evalued when this node is notified that one of the
        #node.attr it's constrained to has changed
        self._constraint = {}

        #if we have a native construct, call it
        if self.tag is not None:
            if hasattr(self,'_construct'):
                self._construct()
        
        #attach all of the other attributes defined in the __init__
        for kw in kwargs:
            #save the attribute as a wf attribute
            self.__wfattrs__[kw] = kwargs[kw]
                
        #call the _init method if we have it
        if hasattr(self,'_init'):
            self._init()
            

    def __repr__(self):
        repr_str = []

        try:
            repr_str.append("<"+self.__tag__+">" + " @ " + str(id(self)))
        except Exception, e:
            repr_str.append('node')

        if hasattr(self,'tag'):
            if self.tag is not None:
                if 'name' in self.tag.keys():
                    repr_str.extend(['name',self.tag.attrib['name']])
                
                if 'on' in self.tag.keys():
                    repr_str.extend(['on',self.tag.attrib['on']])
        
        return string.join(repr_str,' ')

    def __setattr__(self,name,value):
        
        if name in self.__dict__['__wfattrs__'].keys():
            #test to see if it's an attribute defined by an <attribute> tag
            self.__dict__['__wfattrs__'][name] = value
        else:
            #set the value of the attribute in the normal method
            self.__dict__[name] = value

        #update any bindings
        
        #if there are bindings for this attribute

        if hasattr(self,'__bindings__'):
            if self.__bindings__.has_key(name):
                #for each lambda "set" function
                for binding, context in self.__bindings__[name]:
                    #call it and set the value
                    binding(context,value)

        #if there are constraints for this attribute
        if hasattr(self,'__constraints__'):
            if self.__constraints__.has_key(name):
                for node,attr in self.__constraints__[name].values():
                    node.notify(attr)
                    
        
    def __getattr__(self,name):
        #first we need to see if it's a defined wildfire attribute
        if name in self.__wfattrs__.keys():
            #now let's see if it has a getter function
            if name in self.__getters__.keys():
                #if so, get the new value, and store it
                #we don't really need the for loop here, it just makes the code cleaner
                for getter, context in self.__getters__[name]:
                    return getter(context)


            #either way, let's return the value
            return self.__wfattrs__[name]
        
        #raise a similar error if we can't find them!!!!!
        raise AttributeError("'%s' does not exist as a standard or WF attribute" % name)

    def get_siblings(self):
        return self.parent.child_nodes

    def notify(self,attribute):
        try:
            value = self._constraint[attribute]()
            setattr(self,attribute,value)
        except Exception, e:
            print e
            raise ValueError('A notifier is trying to call a constraint the DNE!')

    siblings = property(get_siblings)

class Library(node):
    __tag__ = u'library'

    def _construct(self):        
        #get the module name
        self.module = self.tag.get('library')
        
    def _init(self):
        
        if hasattr(self.parent,'import_path'):
            path = find_lib([self.parent.import_path],self.module)
        else:
            path = find_lib(wildfire.path,self.module)
            
        if path is None:
            raise IOError('Could not locate module (%s)!' % self.module)

        if os.path.basename(path) == '__init__.wfx':
            self.import_path = os.path.dirname(path)
            #if it's a module let's try to automatically recursively load all it's modules
            for f in os.listdir(self.import_path):
                if f != '__init__.wfx':
                    #if it's a file
                    if f.split('.')[-1] == 'wfx':
                        module = string.join(f.split('.')[0:-1],'.')
                        Library(self,module=module)
                    #if it's a directory
                    if os.path.isfile(os.path.join(self.import_path,f,'__init__.wfx')):
                        Library(self,module=f)


                    

        #make sure it's good
        if not os.path.isfile(path):
            raise IOError('Cannot find file: %s!' % path)
        #parse it

        try:
            library_dom = parse(path).getroot()
        except Exception, e:
            print "Error: Could not load Wildfire module (%s)!" % path
            print "The XML parser gave us this error message:"
            print e
            print ""
            raise ImportError('Could not load module %s' % path)
        
        #recursively setup the children
        kiddos = []
        for kiddo in library_dom.getchildren():
            new_kiddo = assemble(kiddo,parent=self,data=self.data)
            if new_kiddo is not None:
                kiddos.append(new_kiddo)

        self.child_nodes.extend(kiddos)

        if self.parent is not None:
            setattr(self.parent,self.module,self)
            
            

class Import(node):
    __tag__ = u'import'
    def _construct(self):
        import basetags
        basetags.__dict__[self.tag.get('module')] = __import__(self.tag.get('module'))

class Wfx(node):
    __tag__ = u'wfx'

class View(node):
    __tag__ = u'view'

class Script(node):
    __tag__ = u'script'

    def __call__(self,event=None):
        try:
            #event should be generic enough for various toolkits to pass event instances.

            #defining names (so you don't have to use nasty old self)
            local_vars = {}
            
            if self.__tag__ == u'handler':
                local_vars['this'] = self.parent
                local_vars['parent'] = self.parent.parent
            else:
                local_vars['this'] = self
                local_vars['parent'] = self.parent
                
            local_vars['doc'] = self.doc
            
            #look for toplevel library nodes and assigning them to easy to access names
            for attribute in self.doc.__dict__:
                if hasattr(self.doc.__dict__[attribute],'import_path'):
                    local_vars[attribute] = self.doc.__dict__[attribute]
                    #exec("%s = doc.__dict__['%s']" % (attribute,attribute))

            for tag in wildfire.tags:
                local_vars[tag.__tag__] = tag
                    
            #executing the handler code
            exec correct_indentation(self.tag.text) in local_vars
            
        except Exception, e:
            #detailed error messages if we blow a bolt
            print "An error occured in WFX embedded code!"
            print "The handler was on='%s'" % self.tag.get('on')
            print "It's parent was %s" % self.parent
            print "The code was..."
            print self.tag.text
            try:
                import traceback
                print "Here's the traceback..."
                traceback.print_exc(file=sys.stdout)
                sys.exit()
            except ImportError:
                sys.exit()

class Handler(Script):
    __tag__ = u'handler'

    def _construct(self):
        #get the handler name
        handler_name = self.tag.get('on')
        #if a list hasn't been setup for this handler
        if not hasattr(self.parent,handler_name):
            #create it
            setattr(self.parent,handler_name,[])
        else:
            #if it is there, and it's not a list
            if not isinstance(getattr(self.parent,handler_name),list):
                #make it into a list with the first item as the old value
                setattr(self.parent,handler_name,[getattr(self.parent,handler_name)])
            
        #append the new handler
        getattr(self.parent,handler_name).append(self)
        



class Attribute(node):
    """The actual attribute tag."""

    __tag__ = u'attribute'

    _name = False
    _instantiate_children = False

    __wfattrs__ = {'name':None}
    
    default = ''

    def _construct(self):
        #get the name of the attribute
        self.name = self.tag.get('name')
        self.default = self.tag.get('default')
        
    def _init(self):
        #mark it as a defined attribute to the class
        if self.parent:
            #assignt the default value to the attribute, the passed value will be populated later
            self.parent.__wfattrs__[self.name] = self.default

# class Dataset(node):
#     __tag__ = u'dataset'
#     def _construct(self):
#         self.data = None

#         try:
#             self.data = eval(self.tag.child_nodes[0].wholeText)
#         except Exception, e:
#             print e

#         if self.data is None:
#             for t in self.tag.childNodes:
#                 if not is_junk(t):
#                     self.data = t
            
    
        
class Class(node):
    __tag__ = u'class'

    _name = False
    _instantiate_children = False
    
    def _construct(self):

        parent_tag = None
        
        #if it's extending something other than view
        if self.tag.get('extends'):
            #get what it's looking for
            search_tag = self.tag.get('extends')
            
            for tag in wildfire.tags:
                #find a match
                if search_tag == tag.__tag__:
                    parent_tag = tag

                    #take all of the nodes from the tag we're extending
                    #target_tag = self.tag.cloneNode(self.tag)
                    #source_tag = parent_tag.tag.cloneNode(parent_tag.tag)
                    
                    
                    #print "SOURCE"
                    #print parent_tag.tag
                    #print parent_tag.tag.toxml()
                    
                    #print "TARGET"
                    #print self.tag
                    #print self.tag.toxml()
                    
                    self.tag = extend(self.tag,parent_tag.tag,attributes=False)
                    #pdb.set_trace()
                    self.tag.attrib.pop('extends')
                    #self.tag.remove_attr('extends')

                    #print "COMBINED"
                    #print self.tag
                    #print self.tag.toxml()

                    #remove the extend tag so we don't recurse?
                    #target_tag.removeAttribute('extends')
                    #hold onto to the combined tag
                    #parent_tag.tag = target_tag
        else:
            #if we're just extending node
            parent_tag = node
        
        if parent_tag is None:
            raise Exception('Could not find super tag %s' % search_tag)

        #create a copy of the class
        #new_class = new.classobj(str(self.tag.get('name')),parent_tag.__bases__, parent_tag.__dict__.copy())
        exec( 'class %s(parent_tag): pass' % self.tag.get('name') )
        exec( 'new_class = %s' % self.tag.get('name') )

        #assign it's new __tag__
        new_class.__tag__ = self.tag.get('name')
        
        #attach the DOM tag
        new_class.tag = self.tag
        
        #replace it if necessary
        for i,tag in enumerate(wildfire.tags):
            if tag.__tag__ == new_class.__tag__:
                wildfire.tags[i] = new_class
                return

        #else just add it to our list of tags
        wildfire.tags.append(new_class)

class Replicate(node):
    __tag__ = u'replicate'
    
    def _construct(self):
        self.data_nodes = []
        self.data = eval(self.tag.get('over'))
        for data in self.data:
            print data
            #self.data_nodes.append([self.tag,data])
            for child_node in self.tag:
                #print child_node
                self.data_nodes.append([child_node,data])
                #new_node = assemble(child_node,self.parent,data=data)
                #self.parent.child_nodes.append(new_node)
                #self.data_nodes.append([new_node,data])
                #print self.data_nodes

    def update(self):
        new_data = eval(self.tag.get('over'))
        if self.data != new_data:
            #print self.data,new_data
            print "Data Changed!"

class EventMapping:
    def __init__(self,native,runtime):
        self.native = native
        self.runtime = runtime

class Event(node):
    __tag__ = u'event'
    def _construct(self):
        self.doc.events.append(EventMapping(self.tag.get('name'),self.tag.get('binding')))

class Method(node):
    __tag__ = u'method'
    def __call__(self,*args):
        #this method can be called
        return self.func(*args)

    def _construct(self):
        #assemble the anonymous function
        #we don't need to name it because that will be handled by the name/id mechanism
        args = self.tag.get('args')
        #import pdb
        #pdb.set_trace()
        if args is None:
            args = ''
        func = ('def wf_temp_func(%s):' % args ) + '\n'
        for line in correct_indentation(self.tag.text).splitlines():
            func += '    ' + line + '\n'
        #execute the function, it's now in the scope
        exec(func)
        
        #save the function as an attribute
        self.func = wf_temp_func

        #import pdb
        #pdb.set_trace()

        if self.tag.get('name'):
            setattr(self.parent,self.tag.get('name'),self)

class Dataset(node):
    __tag__ = u'dataset'

    def _construct(self):
        if self.tag.hasAttribute('src'):
            usock = urllib.urlopen(self.tag.getAttribute('src'))
            #t = ElementTree()
            dom = parse(usock)
            self.data = etree.fromstring(dom.toxml())
            pdb.set_trace()
            usock.close()
        else:
            pdb.set_trace()
