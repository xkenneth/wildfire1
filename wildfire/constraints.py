def bind(attribute, target, func=None):
    """Bind an attribute to the value of another."""
    #set the attributes get_func to call that of another
    
    #if no function is provided assume target is an Attr, and use it's basic get method
    if func is None:
        get_func = lambda obj: obj.get()
    else:
        get_func = func

    attribute.register_get(target,get_func)

    #register the attributes set function to the set functions of the target

    if not func:
        #register the attribute to the target for updates
        target.registered_attributes[attribute.uid] = attribute

        #register the target in the list of registered attributes
        attribute.registered_to = target
    

class Attr(object):
    """Class for handling the getting and setting of an attribute."""
    def __init__(self):
        #the current value of the attribute
        self.value = None

        #the function used retrieving an updated value
        self.get_func = None
        #the context (self) of the get_func
        self.get_context = None
        
        # the function or functions registered to watch updates of said attribute
        #each registered function should provide an object and a lambda function with
        #the object as the first argument and the value as the second for updates
        self.funcs = []

        #the function used for setting the value of an attribute
        self.set_func = None
        #the context (self) of the set_func
        self.set_context = None

        #a dictionary of registered attributes, keyed by UID
        self.registered_attributes = {}
        self.registered_to = None

    def set(self,value):
        """Set the attributes value."""
        #save the value for access
        self.value = value

        #set the value
        if self.set_func is not None:
            self.set_func(self.set_context)

        #update the registered attributes
        for uid in self.registered_attributes:
            self.registered_attributes[uid].set(self.registered_attributes[uid].get())

    def register_set(self,context,func):
        self.set_context = context
        self.set_func = func

        
    def get(self):
        """Return the value of the attribute."""
        #if we've registered a function to handle retrieval of the value
        if self.get_func is not None:
            #access it
            self.value = self.get_func(self.get_context)
            
        return self.value

    def register_get(self,context,func):
        self.get_context = context
        self.get_func = func

    def unbind(self):
        self.registered_to.registered_attributes.pop(self.uid)
        self.registered_to = None
        self.get_func = None
        self.get_context = None
        

if __name__ == '__main__':
    import unittest

    class ConstraintTest(unittest.TestCase):
        def setUp(self):
            uid = 0
            self.master = Attr()
            self.master.uid = uid
            uid += 1
            slaves = []
            for i in range(4):
                slaves.append(Attr())
                slaves[i].uid = uid
                uid += 1
            self.slaves = slaves
        
        def test_bind(self):
            #binding the slaves to the master
            for slave in self.slaves:
                bind(slave,self.master)
            
            #setting the master
            self.master.set(5)
            
            #making sure the slave takes the value of the master
            for slave in self.slaves:
                self.failUnlessEqual(5,slave.get())
                
            #unbinding the slave
            for slave in self.slaves:
                slave.unbind()

            #making sure the slave has nothing leftover from binding
            for slave in self.slaves:
                if len(slave.registered_attributes) != 0:
                    self.fail()
                if slave.registered_to != None:
                    self.fail()

            #testing the get and set functions
            for slave in self.slaves:
                slave.get()

            for slave in self.slaves:
                slave.set(6)

    unittest.main()
                

                
