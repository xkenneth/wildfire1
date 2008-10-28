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
