

from Tkinter import *

def my_handler(event=None):
    print "Hello World!"

master = Tk()

my_button = Button(master,text="Click Me!",
                   command=my_handler)

my_button.grid()

master.mainloop()


