import inspect
import itertools
import networkx
import Operations
import types

def generatorWrapper(node,split,gui,*args):
    if split < 1:
        split = 1
    
    #print args
    if args:
        for arg in itertools.izip(*args):
            for s in range(split):
                yield node.func(gui,*arg)
    else:
        for val in node.func(gui):
            for s in range(split):
                yield val

def listOperators():      
    return [attr for attr in dir(Operations) if isinstance( getattr(Operations,attr,None), types.FunctionType)]
            
def getFuncObj(funcName):
    return getattr(Operations,str(funcName),None)
    
def loadOperators():
    pass