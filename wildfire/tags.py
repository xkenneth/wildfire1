class node:
    pass

class Document(node):
    __tag__ = u'#document'

class Class(node):
    __tag__ = u'class'

tags = [Document,Class]
    
