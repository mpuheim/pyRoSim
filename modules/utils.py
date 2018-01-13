# This Python file uses the following encoding: utf-8

from os import mkdir
#from sys import exc_clear

# struct object definition
class struct():
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# make directory
def makedir(name):
    try:
        mkdir(name) # try to make directory
    except OSError:
        None#exc_clear() # don't show error if directory exists
        # print "Cannot create directory '" + name + "'. Directory already exists."
