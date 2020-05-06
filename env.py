'''
This script contains our environment class
'''
from helper import *
from exp import *
from value import *

class Env:
    '''
    The Env class keeps track of our language's environment
    The content attribute is a list of tuples mapping names to values
    '''
    def __init__(self, content=[]):
        self.content = content
    def __str__(self):
        if not self.content:
            return ''
        output_str = '{ '
        for pair in self.content:
            output_str += str(pair[0]) + ' <- ' + str(pair[1]) + ', '
        output_str = output_str[:-2] + '}'
        return output_str
    def push(self, id, v):
        return Env(self.content + [(id, v)])
    def lookup(self, id):
        for entry in self.content:
            if entry[0] == id:
                return entry[1]
        runtimeError("Runtime error : unbound identifier " + id)
