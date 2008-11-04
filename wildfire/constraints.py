# def bind(attribute, target, func=None):
#     """Bind an attribute to the value of another."""
#     #set the attributes get_func to call that of another
    
#     #if no function is provided assume target is an Attr, and use it's basic get method
#     if func is None:
#         get_func = lambda obj: obj.get()
#     else:
#         get_func = func

#     attribute.register_get(target,get_func)

#     #register the attributes se# t function to the set functions of the target

#     if not func:
#         #register the attribute to the target for updates
#         target.registered_attributes[attribute.uid] = attribute

#         #register the target in the list of registered attributes
#         attribute.registered_to = target

# def bind_set(attribute, target, func):
#     attribute.register_set(target,func)

def bind(tag_node,attr_name,setter,getter=None):
    try:
        #see if a list already exists for the specified attribute
        tag_node.__bindings__[attr_name]
    except KeyError:
        #if not create it
        tag_node.__bindings__[attr_name] = []
        
    #and then append the (lambda) function
    tag_node.__bindings__[attr_name].append(setter)
    
    #if we have a getter function
    if getter:
        tag_node.__getters__[attr_name] = getter

if __name__ == '__main__':
    import unittest

    class ConstraintTest(unittest.TestCase):
        def setUp(self):
            uid = 0
            self.master = Attr(uid)
            uid += 1
            slaves = []
            for i in range(4):
                slaves.append(Attr(uid))
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
                

                
