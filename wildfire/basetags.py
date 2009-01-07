from helper import correct_indentation, extend, find_lib, is_constraint, stuff_dict, call_handlers

from constraints import constrain

from elementtree.ElementTree import parse

import wildfire

import sys, os, string, types

#global
application = None

#meta_nodes = ['attribute','class']

class node:
    """The base class for all other nodes."""

    #the _name attributes designates whether a node type can be given names and ids
    _name = True

    meta_ = False
    
    #if the _instantiate_children flag is true then we instantiate children in the normal way
    _instantiate_children = True
    
    #every base tag has a __tag__ name designating the node
    __tag__ = 'node'
    
    def __init__(self,parent=None,tag=None,data=None,**kwargs):

        
        #
        #    INITIALIZATION
        #

        self.__dict__['self'] = self

        self.__dict__['application'] = application

        #a list of defined attributes
        self.__dict__['wfattrs_'] = []

        #the parent tag of this tag
        self.__dict__['parent'] = parent
        
        #the children of this tag
        self.__dict__['child_nodes'] = []
        
        #data from a replicate
        self.__dict__['data'] = data

        #the actual tag (xml) from which this class tag as instantiated from
        if tag is not None:
            self.__dict__['tag'] = tag
        else:
            if not hasattr(self,'tag'):
                self.__dict__['tag'] = None

        #
        #   HANDLERS
        #
        #  { h_attr:
        #       { listener_node : bound function }
        #  }                

        self.__dict__['senders_'] = {}

        #listeners
        self.__dict__['listeners_'] = {}

        #
        #     NAMES AND IDS
        # 
        
        #if the tag class accepts names, ie, classes don't accept names
        if self._name:
            if self.tag is not None:
                if self.parent is not None:
                    #handling names and ids
                    if self.tag.get('id') is not None:
                        #attaching the node to it's parent as the given id
                        setattr(application,str(self.tag.get('id')),self)
            
                    if self.tag.get('name') is not None:
                        #attaching the node to it's parent as the given name
                        setattr(self.parent,str(self.tag.get('name')),self)
                        self['my_name_'] = self.tag.get('name')
            
        #
        #   CONSTRUCT - FOR INSTANTIATING FROM XML
        # 
                    
        #if we have a native construct and a tag, call it, call it
        #_construct methods are provided to extract required arguments from XML nodes
        if self.tag is not None:
            if hasattr(self,'_construct'):
                self._construct()

        #
        #   KEYWORD ARGUMENTS - FOR INSTANTIATING FROM PYTHON
        #
                
        #keyword arguments take the place of attributes when the classes are instantiated in python instead of in xml
        #attach all of the other attributes defined in the __init__
        for kw in kwargs:
            #save the attribute as a wf attribute
            self.__dict__[kw] = kwargs[kw]
        
        #
        #   BASE CLASS SPECIFIC INIT
        #

        #call the _init method if we have it
        if hasattr(self,'_init'):
            self._init()

        #
        #   CHILD NODES
        #

        #if we don't want to instantiate a node's children, we need to stop now
        if not self._instantiate_children:
            return

        #construct all of the children recursively
        if self.tag:
            for child in self.tag:
                new_child = self.create(child)
                if new_child is not None:
                    self.child_nodes.append(new_child)

        #
        #   ATTRIBUTES & CONSTRAINTS
        #

        #handling given attributes - we need to do this after all of the attribute tags have been executed
        if self is not application:
            if self.tag is not None:
            #for all of the class defined attributes
                for attr in self.wfattrs_:
                    if self.tag.get(attr) is not None:
                        if is_constraint(self.tag.get(attr)):
                        #constrain it!
                            pass
                            # constraint_formula= self.tag.get(attr)[2:-1]
#                             constraint_sources, constraint_statement = constraint_formula.split('->')
#                             constraint_sources = constraint_sources.split(',')

                            
#                             for c_source in constraint_sources:
#                                 source_node = string.join(c_source.split('.')[0:-1],'.')
#                                 source_attr = c_source.split('.')[-1]
                                
#                                 #execute the code with the parent's dict (gives access to names, etc)
#                                 source_node = eval(source_node,self.parent.__dict__)

#                                 constrain(self,attr,source_node,source_attr)
                                
#                             constraint_script = Script(parent=self.parent,python_statement=constraint_statement,evaluate=True)
                            
#                             #constraint_script()
                            
#                             #import pdb
#                             #pdb.set_trace()
                            
#                             #setting up the scope

#                             self._constraint[attr] = constraint_script
#                             self.notify(attr)
                                
#                             #setup_constraints(self,attr,self.tag.get(attr),parent.__dict__)
                            
                        else:
                            attr_val = self.tag.get(attr)
                            
                            #set the value of the attribute
                            setattr(self,attr,attr_val)

        #
        #   HANDLERS
        #
                            
        #only call on the top-most node
        if self is application:
            call_handlers(self)

    def create(self,node,data=None):

        try:
            new_class = wildfire.tags[node.tag]
        except KeyError,e:
            raise KeyError("Class %s not found!" % node.tag)

        
        if hasattr(new_class,'tag'):
            node = extend(node,new_class.tag)

        new_node = new_class(self,node)
        
        new_node.data = data

        if not new_node.meta_:
            return new_node
        

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

        #set the value of the attribute in the normal method
        self.__dict__[name] = value

        #update any bindings
        
        #fire handlers
        #if there are constraints for this attribute
        if self.senders_.has_key(name):
            for node in self.senders_[name]:
                self.senders_[name][node]()
        
    def get_siblings(self):
        """Return the nodes siblings. (including itself!)"""
        return self.parent.child_nodes

    #make siblings accessible as a property
    siblings = property(get_siblings)

    def __getitem__(self, attr):
        """make it possible to get interior nodes dictionary style"""
        return getattr(self, attr)

    def __setitem__(self, attr, val):
        """make it possible to set interior nodes dictionary style"""
        setattr(self, attr, val)


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
        children = []
        for child in library_dom.getchildren():
            new_child = self.create(child,data=self.data)
            if new_child is not None:
                children.append(new_child)

        self.child_nodes.extend(children)

        if self.parent is not None:
            setattr(self.parent,self.module,self)

class Import(node):
    __tag__ = u'import'
    def _construct(self):
        import basetags
        basetags.__dict__[self.tag.get('module')] = __import__(self.tag.get('module'))

class Handler(node):
    __tag__ = u'handler'

    def _construct(self):
        
        self.evaluate = False

        self.python_statement = self.tag.text

        if self.python_statement is None:
            self.python_statement = 'pass'
            
        
        self.on = self.tag.get('on')

        self.arg = self.tag.get('arg')

        if self.arg == None:
            self.arg = 'event=None'

    def _init(self):
        
        func = ('def %s(%s):' % ( self.on, self.arg ) ) + '\n'
        for line in correct_indentation(self.python_statement).splitlines():
            func += '    ' + line + '\n'

        #execute the function, it's now in the scope
        exec func in self.parent.__dict__
        #create the function as a bound method
        #exec "new_bound_method = types.MethodType( new_temp_method, self.parent, wildfire.tags['%s'] )" % ( self.parent.__tag__ ) 
        
        self.parent.senders_[self.on] = {self:self.parent[self.on]}

class Script(Handler):
    __tag__ = u'script'

    def _construct(self):
        Handler._construct(self)
        
        self.on = 'script'

        self.arg = 'event=None'

class Attribute(node):
    """The actual attribute tag."""

    __tag__ = u'attribute'

    _name = False

    _instantiate_children = False

    wfattrs_ = {'name':None}
    
    default = ''

    def _construct(self):
        #get the name of the attribute
        self.name = self.tag.get('name')
        self.default = self.tag.get('default')
        
    def _init(self):
        #mark it as a defined attribute to the class
        if self.parent:
            #assignt the default value to the attribute, the passed value will be populated later
            self.parent.wfattrs_.append(self.name) 
            self.parent[self.name] = self.default

class Class(node):
    __tag__ = u'class'

    _name = False
    _instantiate_children = False
    
    def _construct(self):

        parent_tag = None
        
        #if it's extending something other than view
        if self.tag.get('extends'):
            #get what it's looking for
            # search_tag = self.tag.get('extends')
            
#             for tag in wildfire.tags:
#                 #find a match
#                 if search_tag == tag.__tag__:
#                     parent_tag = tag

#                     self.tag = extend(self.tag,parent_tag.tag,attributes=False)
#                     self.tag.attrib.pop('extends')

            parent_tag = wildfire.tags[self.tag.get('extends')]

            self.tag = extend(self.tag,wildfire.tags[self.tag.get('extends')].tag,attributes=False)

        else:
            #if we're just extending node
            parent_tag = node
        
        if parent_tag is None:
            raise Exception('Could not find super tag %s' % search_tag)

        #create a copy of the class
        #new_class = new.classobj(str(self.tag.get('name')),parent_tag.__bases__, parent_tag.__dict__.copy())
        
        if self.tag.get('extends') is None:
            parent_tag = node
        else:
            parent_tag = wildfire.tags[self.tag.get('extends')]
            
        new_class = type(self.tag.get('name'),(parent_tag,object),{})

        #assign it's new __tag__
        new_class.__tag__ = self.tag.get('name')
        
        #attach the DOM tag
        new_class.tag = self.tag

        #replace it if necessary
        #for i,tag in enumerate(wildfire.tags):
        #    if tag.__tag__ == new_class.__tag__:
        #        wildfire.tags[i] = new_class
        #        return

        wildfire.tags[self.tag.get('name')] = new_class

        #else just add it to our list of tags
        #wildfire.tags.append(new_class)

class Replicate(node):
    __tag__ = u'replicate'
    
    def _construct(self):
        self.data_nodes = []

        self.data = eval(self.tag.get('over'))

        for data in self.data:
            #self.data_nodes.append([self.tag,data])
            for child_node in self.tag:
                self.data_nodes.append([child_node,data])
                #new_node = assemble(child_node,self.parent,data=data)
                #self.parent.child_nodes.append(new_node)
                #self.data_nodes.append([new_node,data])
                #print self.data_nodes

    def update(self):
        new_data = eval(self.tag.get('over'))
        if self.data != new_data:
            print "Data Changed!"

#
# METHOD
#
# creates a bound method on the parent class

class Method(node):
    __tag__ = u'method'
    meta_ = True

    def _construct(self):
        #assemble the anonymous function
        #we don't need to name it because that will be handled by the name/id mechanism
        args = self.tag.get('args')

        if args is None:
            args = ''

        self.args = args

        self.name = self.tag.get('name')

    def _init(self):

        #create the function text with the proper indentation
        func = ('def %s(%s):' % ( self.name,self.args ) ) + '\n'
        for line in correct_indentation(self.tag.text).splitlines():
            func += '    ' + line + '\n'

        #execute the function, it's now in the scope

        exec func in self.parent.__dict__

