if __name__ == '__main__':
    import unittest
    
    from wildfire.tags import *

    from wildfire.constraints import bind, unbind

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
            
    class Bindings(unittest.TestCase):
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

            
    unittest.main()

