import itertools
import networkx
import Operations
import types

def generatorWrapper(func,split,gui,*args):
    func.gui = gui
    if split < 1:
        split = 1
    #print args
    if args:
        for arg in itertools.izip(*args):
            for s in range(split):
                yield func(*arg)
    else:
        for val in func():
            for s in range(split):
                yield val

def listOperators():      
    return [attr for attr in dir(Operations) if isinstance( getattr(Operations,attr,None), types.FunctionType)]
            
def getFuncObj(funcName):
    return getattr(Operations,str(funcName),None)
    
def loadOperators():
    pass