if __name__ == '__main__':
    import unittest
    
    from wildfire.tags import *

    from wildfire.constraints import bind, unbind, constrain, unconstrain, setup_constraints

    class Variable:
        """A dummy class that allows you to get and set a variable, used for testing purposes."""
        def __init__(self,value):
            self.value = value

        def set(self,value):
            self.value = value

        def get(self):
            return self.value

    class TestNode(unittest.TestCase):
        def setUp(self):
            #test the instantiation of a node
            
            node()

        def testSetUp(self):
            pass

        def testKwargs(self):

            t = node(test=1)

            self.failUnlessEqual(t.test,1)

    class TestAttribute(unittest.TestCase):
        def setUp(self):
            self.test_attribute = Attribute(name='Test')

        def testSetUp(self):
            pass

        def testName(self):
            self.failUnlessEqual(self.test_attribute.name,'Test')
            
    class TestBindings(unittest.TestCase):
        def setUp(self):
            #set up two nodes for testing
            self.test_node = node()
            #define an attribute on the test_node
            Attribute(self.test_node,name='that')

            self.test_variable = Variable(4)
            
        def testSetUp(self):
            pass

        def testBind(self):
            #bind the test_node to the test_variable
            bind(self.test_node,'that',lambda obj, v: obj.set(v), self.test_variable, lambda obj: obj.get(), self.test_variable)
            
            #now the value of that attribute should be 4
            self.failUnlessEqual(self.test_node.that,4)
            
            #now set the test_variable, the attribute on the node should also change
            self.test_variable.set(5)
            
            self.failUnlessEqual(self.test_node.that,5)
            
            #now set the node, the attribute should also change

            self.test_node.that = 6
            
            self.failUnlessEqual(self.test_variable.value,6)

            #so far so good, looks like things are working

            #let's test the unbind function
            
            unbind(self.test_node,'that')
            
            self.failUnlessEqual(self.test_node.__bindings__['that'],[])
            self.failUnlessEqual(self.test_node.__getters__['that'],[])

            #and it looks like we're good

    class TestConstraints(unittest.TestCase):
        def setUp(self):
            #set up three test nodes and some dummy attributes
            self.test_node_a = node()
            Attribute(self.test_node_a,name='test')
            
            self.test_node_b = node()
            Attribute(self.test_node_b,name='source_b')
            
            self.test_node_c = node()
            Attribute(self.test_node_c,name='source_c')

        def testSetUp(self):
            pass

        def testComplexConstraints(self):
            #In this test we're going to constrain test_node_a.test to test_node_b.source_b and test_node_c.source_c
            
            #our test function
            t = lambda: self.test_node_b.source_b + self.test_node_c.source_c

            #set up some default values
            self.test_node_a.test = 1
            self.test_node_b.source_b = 2
            self.test_node_c.source_c = 3

            #set up the constraints
            constrain(self.test_node_a,'test',self.test_node_b,'source_b')
            constrain(self.test_node_a,'test',self.test_node_c,'source_c')

            #assign the function to test_node_a
            self.test_node_a._constraint['test'] = t

            #notify the node
            self.test_node_a.notify('test')
            
            #now our constraints are setup and initialized, let's make sure he's the proper value
            
            self.failUnlessEqual(self.test_node_a.test,5)

            #now let's change each constraint 
            self.test_node_b.source_b = 3

            self.failUnlessEqual(self.test_node_a.test,6)

            self.test_node_c.source_c = 4

            self.failUnlessEqual(self.test_node_a.test,7)

            #and finally unconstrain our element
            unconstrain(self.test_node_a,'test')

            self.failUnlessEqual(self.test_node_a.__constrained_to__['test'],{})
            self.failUnlessEqual(self.test_node_b.__constraints__['source_b'],{})
            self.failUnlessEqual(self.test_node_c.__constraints__['source_c'],{})

            
        def testConstraintString(self):

            test_node_a = self.test_node_a
            test_node_b = self.test_node_b
            test_node_c = self.test_node_c

            #set up some default values
            self.test_node_a.test = 1
            self.test_node_b.source_b = 2
            self.test_node_c.source_c = 3
            
            cstring = '${test_node_b.source_b + test_node_c.source_c}'
            
            setup_constraints(test_node_a,'test',cstring,locals())

            #now our constraints are setup and initialized, let's make sure he's the proper value
            
            self.failUnlessEqual(self.test_node_a.test,5)

            #now let's change each constraint 
            self.test_node_b.source_b = 3

            self.failUnlessEqual(self.test_node_a.test,6)

            self.test_node_c.source_c = 4

            self.failUnlessEqual(self.test_node_a.test,7)

            #and finally unconstrain our element
            unconstrain(self.test_node_a,'test')

            self.failUnlessEqual(self.test_node_a.__constrained_to__['test'],{})
            self.failUnlessEqual(self.test_node_b.__constraints__['source_b'],{})
            self.failUnlessEqual(self.test_node_c.__constraints__['source_c'],{})

            
        
        
            

            
    unittest.main()

