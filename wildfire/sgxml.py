### sgxml.py ###
### The purpose of this class is to provide an XML dom that notifys the fact that ###
### it's been modified! ###
### Kenneth Miller ###
### xkenneth@gmail.com ###

from gxml import gxml

def notify_wrapper(func):
    def new_func(self,*args,**kwargs):
        self.notify()
        return func(self,*args,**kwargs)
    return new_func

class sgxml(gxml):
    def __init__(self,*args,**kwargs):
        self.notify_func = None
        self.notify_context = None
        
        gxml.__init__(self,*args,**kwargs)

    def notify(self):
        if self.notify_context:
            return self.notify_func(self.notify_context)
        if self.notify_func:
            return self.notify_func()
        

    def register_notify(self,func,context=None):
        self.notify_func = func
        self.notify_context = context

    from_string = notify_wrapper(gxml.from_string)

    parse = notify_wrapper(gxml.parse)
    
    set = notify_wrapper(gxml.set)
    
    remove_attr = notify_wrapper(gxml.remove_attr)
    
    set_text = notify_wrapper(gxml.set_text)

    append = notify_wrapper(gxml.append)

    
if __name__ == '__main__':
    
    import unittest
    
    class Test(unittest.TestCase):
        def setUp(self):
            self.inst = sgxml()

        def test_inst(self):

            
            pass

    unittest.main()
                     
