### sgxml.py ###
### The purpose of this class is to provide an XML dom that notifys the fact that ###
### it's been modified! ###
### Kenneth Miller ###
### xkenneth@gmail.com ###

from gxml import gxml, to_string
def bottom_up(xml_node):
    for child_node in xml_node.child_nodes:
        bottom_up(child_node)

    xml_node.notify()

    for key in xml_node.keys():
        xml_node.get(key).notify()
    
    
def notify_wrapper(func):
    def new_func(self,*args,**kwargs):
        bottom_up(self)
        return func(self,*args,**kwargs)
    return new_func

class notifier(object):
    def register_notify(self,func):
        self.__notify__.append(func)

class attribute_node(object):
    def __init__(self,name,value,parent):
        self.name = name
        self.value = value
        self.parent = parent

    def register_notify(self,func):
        try:
            self.parent.__attr_notify__[self.name]
        except KeyError:
            self.parent.__attr_notify__[self.name] = []

        self.parent.__attr_notify__[self.name].append(func)

    def notify(self):
        try:
            for notify_func in self.parent.__attr_notify__[self.name]:
                notify_func()
        except KeyError:
            pass
            

class sgxml(gxml,notifier):
    def __init__(self,*args,**kwargs):
        self.__notify__ = []
        self.__attr_notify__ = {}

        gxml.__init__(self,*args,**kwargs)

    def notify(self):
        #for all of the notification functions
        for notify_func in self.__notify__:
            #call them
            notify_func()
            
        
    set = notify_wrapper(gxml.set)
    
    remove_attr = notify_wrapper(gxml.remove_attr)
    
    set_text = notify_wrapper(gxml.set_text)

    append = notify_wrapper(gxml.append)

    def get(self,attribute):
        return attribute_node(attribute,gxml.get(self,attribute),self)

    
        

    
if __name__ == '__main__':
    
    import unittest

    class TestClass(object):
        def __init__(self):
            self.val = 0

        def notify(self):
            self.val += 1
    
    class Test(unittest.TestCase):
        def setUp(self):
            self.inst = sgxml()
            self.inst.from_string("<a this='that'><b/></a>")

        def test_inst(self):
            pass

        def test_attr_access(self):
            self.failIf(not isinstance(self.inst.get('this'),attribute_node))

        def test_notify(self):
            #to track our notifications
            t = TestClass()

            #register the a node
            self.inst.register_notify(t.notify)

            #modify the a node
            self.inst.set('a','1')
            
            #it should have fired
            self.failUnlessEqual(t.val,1)

            #register the b node
            self.inst.child_nodes[0].register_notify(t.notify)
            
            #register the this attribute
            self.inst.get('this').register_notify(t.notify)

            #register the a attribute
            self.inst.get('a').register_notify(t.notify)
            
            #now 4 attributes should fire when modify the a node again
            self.inst.set('b','2')

            self.failUnlessEqual(t.val,5)

            
            
            
            
            
               
        

    unittest.main()
                     
